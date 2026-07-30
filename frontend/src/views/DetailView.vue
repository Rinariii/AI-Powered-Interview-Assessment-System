<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import {
    ArrowLeft,
    User,
    Calendar,
    Video,
    Clock,
    Share2,
    Download
} from "lucide-vue-next"
import { useShare } from '@vueuse/core';

import AppHeader from "@/components/shared/AppHeader.vue"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils";
import { Badge } from '@/components/ui/badge'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import AppScoreGauge from "@/components/shared/AppScoreGauge.vue";
import AssessmentCard from "@/components/shared/AppAssessmentCard.vue";
import { supabase } from '@/lib/supabaseClient';
import type { AssessmentReport, VideoAssessment } from "@/types/assessment";

const route = useRoute();
const { share } = useShare()

const report = ref<AssessmentReport | null>(null);
const isLoading = ref(true);

const fetchAssessment = async () => {
    try {
        const { data, error } = await supabase
            .from('assessments')
            .select(`
                *,
                assessment_videos (*)
            `)
            .eq('id', route.params.id)
            .single();

        if (error) throw error;

        report.value = {
            id: data.id,
            generated_at: data.generated_at || data.created_at,
            total_videos: data.total_videos,
            candidate_name: data.candidate_name,
            position: data.position,
            videos: (data.assessment_videos || []).map((video: any) => ({
                video_id: video.video_sequence,
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
            } as VideoAssessment))
        };
    } catch (error) {
        console.error('Error fetching assessment:', error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchAssessment();
});

const averageScore = computed(() => {
    if (!report.value || !report.value.videos.length) return "0.0";
    return (
        report.value.videos.reduce((acc, v) => acc + v.final_score, 0) / report.value.videos.length
    ).toFixed(1);
});

const averageFluency = computed(() => {
    if (!report.value || !report.value.videos.length) return "0.0";
    return (
        report.value.videos.reduce((acc, v) => acc + v.fluency_score, 0) / report.value.videos.length
    ).toFixed(1);
});

const totalDuration = computed(() => {
    if (!report.value) return 0;
    return report.value.videos.reduce((acc, v) => acc + v.duration_sec, 0);
});

const totalPauses = computed(() => {
    if (!report.value) return 0;
    return report.value.videos.reduce((acc, v) => acc + (v.pauses ? v.pauses.length : 0), 0);
});

const uniqueAiLabels = computed(() => {
    if (!report.value) return [];
    const labels = report.value.videos.map(v => v.ai_likeness_label);
    return [...new Set(labels)];
});

const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
};

const shareReport = () => {
    share({
        title: 'Assessment Report',
        text: 'Check out this assessment report',
        url: route.fullPath
    })
}
</script>

<template>
    <div class="min-h-screen bg-background">
        <AppHeader />

        <main class="container mx-auto py-8">
            <!-- Back Button -->
            <Button variant="ghost" class="mb-6" asChild>
                <RouterLink to="/">
                    <ArrowLeft class="mr-2 h-4 w-4" />
                    Back to Dashboard
                </RouterLink>
            </Button>

            <div v-if="isLoading" class="flex justify-center items-center py-20">
                <p class="text-muted-foreground">Loading assessment details...</p>
            </div>

            <div v-else-if="report">
                <Card class="mb-8">
                    <CardHeader>
                        <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                            <div class="space-y-4">
                                <div class="space-y-2">
                                    <div class="flex items-center gap-2">
                                        <User class="h-5 w-5 text-muted-foreground" />
                                        <h1 class="text-2xl font-bold">
                                            {{ report.candidate_name || `Assessment #${report.id}` }}
                                        </h1>
                                    </div>
                                    <Badge v-if="report.position" variant="secondary" class="text-sm">
                                        {{ report.position }}
                                    </Badge>
                                </div>

                                <div class="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                                    <span class="flex items-center gap-1">
                                        <Calendar class="h-4 w-4" />
                                        {{ formatDate(report.generated_at) }}
                                    </span>
                                    <span class="flex items-center gap-1">
                                        <Video class="h-4 w-4" />
                                        {{ report.total_videos }} video{{ report.total_videos > 1 ? "s" : "" }}
                                    </span>
                                    <span class="flex items-center gap-1">
                                        <Clock class="h-4 w-4" />
                                        {{ formatDuration(totalDuration) }} total
                                    </span>
                                </div>
                            </div>

                            <div class="flex gap-2">
                                <Button variant="outline" size="sm" @click="shareReport">
                                    <Share2 class="mr-2 h-4 w-4" />
                                    Share
                                </Button>
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent>
                        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                            <div class="flex items-center gap-4 border p-4">
                                <AppScoreGauge :score="Number(averageScore)" label="" size="sm" />
                                <div>
                                    <p class="text-sm text-muted-foreground">Avg. Score</p>
                                    <p class="text-2xl font-bold">{{ averageScore }}/5</p>
                                </div>
                            </div>

                            <div class="flex items-center gap-4 border p-4">
                                <AppScoreGauge :score="Number(averageFluency)" label="" size="sm" />
                                <div>
                                    <p class="text-sm text-muted-foreground">Avg. Fluency</p>
                                    <p class="text-2xl font-bold">{{ averageFluency }}/5</p>
                                </div>
                            </div>

                            <div class="flex flex-col justify-center border p-4">
                                <p class="text-sm text-muted-foreground">Total Pauses</p>
                                <p class="text-2xl font-bold">
                                    {{ totalPauses }}
                                </p>
                            </div>

                            <div class="flex flex-col justify-center border p-4">
                                <p class="text-sm text-muted-foreground">AI Detection</p>
                                <div class="flex flex-wrap gap-1 mt-1">
                                    <Badge v-for="label in uniqueAiLabels" :key="label" variant="outline"
                                        class="text-xs">
                                        {{ label }}
                                    </Badge>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <!-- Video Assessments -->
                <div class="space-y-6">
                    <h2 class="text-xl font-semibold">Video Assessments</h2>
                    <AssessmentCard v-for="video in report.videos" :key="video.video_id" :assessment="video"
                        showDetails />
                </div>
            </div>

            <div v-else class="text-center py-20">
                <p class="text-muted-foreground">Assessment not found</p>
            </div>
        </main>
    </div>
</template>