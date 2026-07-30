<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ArrowRight, Clock, TrendingUp, Users, Video } from "lucide-vue-next"
import AppHeader from "@/components/shared/AppHeader.vue"
import StatsCard from "@/components/home/StatsCard.vue"
import { Button } from "@/components/ui/button"
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent
} from '@/components/ui/card'
import { formatDate } from "@/lib/utils"
import { Badge } from '@/components/ui/badge'
import type { AssessmentReport, VideoAssessment } from "@/types/assessment"
import AssessmentCard from "@/components/shared/AppAssessmentCard.vue"
import { supabase } from '@/lib/supabaseClient'

const assessments = ref<AssessmentReport[]>([]);

const fetchAssessments = async () => {
    const { data, error } = await supabase
        .from('assessments')
        .select(`
            *,
            assessment_videos (*)
        `)
        .order('created_at', { ascending: false });

    if (error) {
        console.error('Error fetching assessments:', error);
        return;
    }

    assessments.value = data.map((item: any) => ({
        id: item.id,
        generated_at: item.generated_at || item.created_at,
        total_videos: item.total_videos,
        candidate_name: item.candidate_name,
        position: item.position,
        videos: (item.assessment_videos || []).map((video: any) => ({
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
    }));
};

onMounted(() => {
    fetchAssessments();
});

// --- Computed Stats ---
const totalAssessmentsCount = computed(() => assessments.value.length);

const uniqueCandidatesCount = computed(() => {
    const names = assessments.value.map(a => a.candidate_name).filter(Boolean);
    return new Set(names).size;
});

const averageFinalScore = computed(() => {
    const allVideos = assessments.value.flatMap(a => a.videos);
    if (!allVideos.length) return "0.0";
    const total = allVideos.reduce((acc, v) => acc + v.final_score, 0);
    return (total / allVideos.length).toFixed(1);
});

const averageDuration = computed(() => {
    const allVideos = assessments.value.flatMap(a => a.videos);
    if (!allVideos.length) return "0 min";
    const totalSeconds = allVideos.reduce((acc, v) => acc + v.duration_sec, 0);
    const avgSeconds = totalSeconds / allVideos.length;
    return (avgSeconds / 60).toFixed(1) + " min";
});
</script>

<template>
    <div class="min-h-screen bg-background">
        <AppHeader />

        <main class="container mx-auto py-8">
            <!-- Hero Section -->
            <section class="mb-12">
                <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                    <div class="space-y-2">
                        <h1 class="text-3xl font-bold tracking-tight md:text-4xl">
                            Interview Dashboard
                        </h1>
                        <p class="text-muted-foreground max-w-2xl">
                            AI-powered interview assessment system. Upload candidate videos,
                            analyze responses, and get objective evaluations in minutes.
                        </p>
                    </div>
                </div>
            </section>

            <!-- Stats Grid -->
            <section class="mb-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatsCard title="Total Assessments" :value="totalAssessmentsCount" :icon="Video" />
                <StatsCard title="Unique Candidates" :value="uniqueCandidatesCount" :icon="Users"
                    description="Total evaluated" />
                <StatsCard title="Avg. Final Score" :value="averageFinalScore" :icon="TrendingUp"
                    description="Out of 5.0" />
                <StatsCard title="Avg. Video Duration" :value="averageDuration" :icon="Clock" description="Per video" />
            </section>

            <!-- Recent Assessments -->
            <section class="space-y-6">
                <div class="flex items-center justify-between">
                    <div class="space-y-1">
                        <h2 class="text-2xl font-semibold tracking-tight">
                            Recent Assessments
                        </h2>
                        <p class="text-sm text-muted-foreground">
                            Latest candidate evaluations and analysis results
                        </p>
                    </div>
                </div>

                <div class="grid gap-6">
                    <Card v-for="report in assessments" :key="report.id" class="overflow-hidden">
                        <CardHeader class="border-b bg-muted/30">
                            <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div class="space-y-1">
                                    <CardTitle class="text-lg">
                                        {{ report.candidate_name || `Assessment #${report.id}` }}
                                    </CardTitle>

                                    <div class="flex items-center gap-2 text-sm text-muted-foreground">
                                        <Badge v-if="report.position" variant="secondary">
                                            {{ report.position }}
                                        </Badge>

                                        <span>•</span>
                                        <span>{{ formatDate(report.generated_at) }}</span>
                                        <span>•</span>
                                        <span>{{ report.total_videos }} video{{ report.total_videos > 1 ? "s" : ""
                                        }}</span>
                                    </div>
                                </div>

                                <Button variant="outline" size="sm" as-child>
                                    <RouterLink :to="`/assessment/${report.id}`">
                                        View Details
                                        <ArrowRight class="ml-2 h-4 w-4" />
                                    </RouterLink>
                                </Button>
                            </div>
                        </CardHeader>

                        <CardContent class="p-0">
                            <div class="divide-y">
                                <div v-for="video in report.videos.slice(0, 1)" :key="video.video_id" class="p-6">
                                    <AssessmentCard :assessment="video" @view-details="() => { }" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </section>
        </main>
    </div>
</template>