<script setup lang="ts">
import { Brain, FileVideo, Zap, BarChart3 } from 'lucide-vue-next'

import AppHeader from '@/components/shared/AppHeader.vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import VideoUploader from '@/components/upload/VideoUploader.vue';
import { ref } from 'vue';
import { toast } from 'vue-sonner';
import { useRouter } from 'vue-router';
import type { VideoUpload } from '@/types/assessment';
import { analyzeVideos } from '@/services/analysis';

const features = [
    {
        icon: Brain,
        title: "AI-Powered Analysis",
        description: "Advanced NLP evaluates responses for relevance and quality"
    },
    {
        icon: FileVideo,
        title: "Video Processing",
        description: "Automatic speech-to-text transcription with timeline"
    },
    {
        icon: Zap,
        title: "Fast Results",
        description: "Get comprehensive assessments in under 2x video duration"
    },
    {
        icon: BarChart3,
        title: "Detailed Metrics",
        description: "Fluency, AI detection, semantic scoring, and more"
    }
];

const instructions = [
    "Upload interview video files (.mp4, .webm supported)",
    "Provide the interview question for each video",
    "Define the rubric/criteria for evaluation",
    "Submit for AI analysis and receive detailed assessment"
];

const router = useRouter();

const candidateName = ref('');
const jobPosition = ref('');

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { supabase } from '@/lib/supabaseClient';

const isLoading = ref(false);

const handleSubmit = async (files: VideoUpload[]) => {
    if (!candidateName.value.trim()) {
        toast({
            title: "Validation Error",
            description: "Please enter a candidate name",
            variant: "destructive"
        });
        return;
    }

    isLoading.value = true;

    try {
        const result = await analyzeVideos(files);

        // 1. Insert into assessments table
        const { data: assessmentData, error: assessmentError } = await supabase
            .from('assessments')
            .insert({
                candidate_name: candidateName.value,
                position: jobPosition.value,
                total_videos: result.total_videos,
                generated_at: result.generated_at
            })
            .select()
            .single();

        if (assessmentError) throw assessmentError;
        if (!assessmentData) throw new Error("Failed to create assessment");

        const assessmentId = assessmentData.id;

        // 2. Insert into assessment_videos table
        const videosToInsert = result.videos.map(video => ({
            assessment_id: assessmentId,
            video_sequence: video.video_id,
            file_path: video.file_path,
            question: video.question,
            final_score: video.final_score,
            rubric_reason: video.rubric_reason,
            fluency_score: video.fluency_score,
            ai_likeness_label: video.ai_likeness_label,
            ai_silence_score: video.ai_silence_score,
            full_transcript: video.full_transcript,
            segments: video.segments,
            pauses: video.pauses,
            duration_sec: video.duration_sec
        }));

        const { error: videosError } = await supabase
            .from('assessment_videos')
            .insert(videosToInsert);

        if (videosError) throw videosError;

        toast({
            title: "Analysis Complete",
            description: `Successfully analyzed and saved ${files.length} video${files.length > 1 ? "s" : ""}.`,
        });

        router.push(`/assessment/${assessmentId}`);
    } catch (error) {
        toast({
            title: "Analysis Failed",
            description: error instanceof Error ? error.message : "An error occurred during analysis",
            variant: "destructive"
        });
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div class="min-h-screen bg-background">
        <AppHeader />

        <main class="container mx-auto py-8">
            <div class="mx-auto max-w-4xl space-y-8">
                <!-- Header -->
                <div class="space-y-2">
                    <h1 class="text-3xl font-bold tracking-tight">
                        Upload Interview Videos
                    </h1>
                    <p class="text-muted-foreground">
                        Upload candidate interview recordings with questions and rubrics for AI-powered assessment.
                    </p>
                </div>

                <!-- Features Grid -->
                <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <Card v-for="feature in features" :key="feature.title" class="bg-muted/30">
                        <CardContent class="flex items-start gap-3 p-4">
                            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                <component :is="feature.icon" class="h-5 w-5 text-primary" />
                            </div>
                            <div class="space-y-1">
                                <p class="font-medium text-sm">{{ feature.title }}</p>
                                <p class="text-xs text-muted-foreground">
                                    {{ feature.description }}
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <!-- Upload Section -->
                <Card>
                    <CardHeader>
                        <CardTitle>Video Upload</CardTitle>
                        <CardDescription>
                            Upload one or more interview videos. Each video requires a question and evaluation rubric.
                        </CardDescription>
                    </CardHeader>
                    <CardContent class="space-y-6">
                        <div class="grid gap-4 md:grid-cols-2">
                            <div class="space-y-2">
                                <Label for="candidateName">Candidate Name</Label>
                                <Input id="candidateName" v-model="candidateName" placeholder="Enter candidate name" />
                            </div>
                            <div class="space-y-2">
                                <Label for="jobPosition">Job Position</Label>
                                <Input id="jobPosition" v-model="jobPosition"
                                    placeholder="Enter target position (optional)" />
                            </div>
                        </div>

                        <VideoUploader @submit="handleSubmit" :isLoading="isLoading" />
                    </CardContent>
                </Card>

                <!-- Instructions -->
                <Card class="bg-muted/30">
                    <CardHeader>
                        <CardTitle class="text-lg">How It Works</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ol class="space-y-4">
                            <li v-for="(step, index) in instructions" :key="index" class="flex items-start gap-3">
                                <div
                                    class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-medium text-primary-foreground">
                                    {{ index + 1 }}
                                </div>
                                <span class="text-sm text-muted-foreground pt-0.5">{{ step }}</span>
                            </li>
                        </ol>
                    </CardContent>
                </Card>
            </div>
        </main>
    </div>
</template>