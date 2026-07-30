<script setup lang="ts">
import { computed } from 'vue'
import {
    FileVideo,
    MessageSquare,
    Bot,
    Target,
    Mic,
    AlertCircle
} from 'lucide-vue-next'
import { cn } from '@/lib/utils'

// Components
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import AppScoreGauge from '@/components/shared/AppScoreGauge.vue'
import AppTranscriptViewer from '@/components/shared/AppTranscriptViewer.vue'
import type { VideoAssessment } from '@/types/assessment'

// --- Props & Emits ---
const props = withDefaults(defineProps<{
    assessment: VideoAssessment
    showDetails?: boolean
    // Optional: If you want to explicitly control button visibility based on parent handler
    hasViewDetailsHandler?: boolean
}>(), {
    showDetails: false,
    hasViewDetailsHandler: true
})

const emit = defineEmits<{
    (e: 'view-details'): void
}>()

// --- Logic ---

// Computed property to transform tuple segments into objects
// This is more efficient than doing it in the template
const formattedSegments = computed(() => {
    return props.assessment.segments.map(([start, end, text]) => ({
        start,
        end,
        text
    }))
})

const getAILikenessColor = (label: string) => {
    const l = label.toLowerCase()
    if (l.includes("not")) return "bg-green-500/10 text-green-600 border-green-500/20"
    if (l.includes("somewhat")) return "bg-yellow-500/10 text-yellow-600 border-yellow-500/20"
    return "bg-red-500/10 text-red-600 border-red-500/20"
}

const getFinalScoreColor = (score: number) => {
    if (score >= 4) return "text-green-600"
    if (score >= 3) return "text-yellow-600"
    if (score >= 2) return "text-orange-600"
    return "text-red-600"
}
</script>

<template>
    <Card class="overflow-hidden">
        <CardHeader class="border-b bg-muted/30 pb-4">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div class="flex items-start gap-3">
                    <div class="flex h-10 w-10 items-center justify-center bg-primary/10">
                        <FileVideo class="h-5 w-5 text-primary" />
                    </div>
                    <div class="space-y-1">
                        <p class="font-medium text-sm text-muted-foreground">
                            Video #{{ assessment.video_id }}
                        </p>
                        <p class="text-xs text-muted-foreground truncate max-w-[200px]">
                            {{ assessment.file_path }}
                        </p>
                    </div>
                </div>

                <div class="flex items-center gap-2">
                    <Badge variant="outline" :class="cn(getAILikenessColor(assessment.ai_likeness_label))">
                        <Bot class="mr-1 h-3 w-3" />
                        {{ assessment.ai_likeness_label }}
                    </Badge>
                    <div :class="cn('text-2xl font-bold', getFinalScoreColor(assessment.final_score))">
                        {{ assessment.final_score }}/5
                    </div>
                </div>
            </div>
        </CardHeader>

        <CardContent class="p-6 space-y-6">
            <div class="space-y-2">
                <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <MessageSquare class="h-4 w-4" />
                    Interview Question
                </div>
                <p class="text-sm bg-muted/50 p-3 border">
                    {{ assessment.question }}
                </p>
            </div>

            <div class="grid grid-cols-2 gap-6 sm:grid-cols-4">
                <AppScoreGauge :score="assessment.final_score" label="Final Score" size="sm" />
                <AppScoreGauge :score="assessment.fluency_score" label="Fluency" size="sm" />
                <AppScoreGauge :score="assessment.ai_silence_score" label="Naturalness" size="sm" />
                <div class="flex flex-col items-center gap-2">
                    <div class="flex h-20 w-20 items-center justify-center rounded-full bg-muted">
                        <Mic class="h-8 w-8 text-muted-foreground" />
                    </div>
                    <span class="text-sm font-medium text-muted-foreground text-center">
                        {{ assessment.pauses.length }} Pauses
                    </span>
                </div>
            </div>

            <div class="space-y-2">
                <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Target class="h-4 w-4" />
                    Rubric Evaluation
                </div>
                <div class="flex items-start gap-2 border border-amber-500/20 bg-amber-500/5 p-3">
                    <AlertCircle class="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                    <p class="text-sm text-amber-800 dark:text-amber-200">
                        {{ assessment.rubric_reason }}
                    </p>
                </div>
            </div>

            <AppTranscriptViewer v-if="showDetails" :transcript="assessment.full_transcript"
                :segments="formattedSegments" :pauses="assessment.pauses" :duration="assessment.duration_sec" />
        </CardContent>
    </Card>
</template>