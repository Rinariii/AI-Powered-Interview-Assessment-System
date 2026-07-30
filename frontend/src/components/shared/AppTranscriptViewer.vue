<script setup lang="ts">
import { ref } from 'vue'
import { Clock, Pause, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

// UI Components
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

// --- Types ---
interface Segment {
    start: number
    end: number
    text: string
}

interface Props {
    transcript: string
    segments: Segment[]
    pauses: number[]
    duration: number
}

// --- Props & State ---
defineProps<Props>()

const isExpanded = ref(false)
const viewMode = ref<"full" | "segments">("segments")

// --- Helpers ---
const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, "0")}`
}
</script>

<template>
    <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-4">
            <div class="space-y-1">
                <CardTitle class="text-lg">Transcript</CardTitle>
                <div class="flex items-center gap-4 text-sm text-muted-foreground">
                    <span class="flex items-center gap-1">
                        <Clock class="h-4 w-4" />
                        {{ formatTime(duration) }} duration
                    </span>
                    <span class="flex items-center gap-1">
                        <Pause class="h-4 w-4" />
                        {{ pauses.length }} pause{{ pauses.length !== 1 ? "s" : "" }} detected
                    </span>
                </div>
            </div>

            <div class="flex gap-2">
                <Button :variant="viewMode === 'segments' ? 'default' : 'outline'" size="sm"
                    @click="viewMode = 'segments'">
                    Timeline
                </Button>
                <Button :variant="viewMode === 'full' ? 'default' : 'outline'" size="sm" @click="viewMode = 'full'">
                    Full Text
                </Button>
            </div>
        </CardHeader>

        <CardContent class="space-y-4">
            <div v-if="viewMode === 'full'" :class="cn(
                'relative overflow-hidden transition-all duration-300',
                !isExpanded && 'max-h-40'
            )">
                <p class="text-sm leading-relaxed">{{ transcript }}</p>

                <div v-if="!isExpanded"
                    class="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-card to-transparent" />
            </div>

            <div v-else :class="cn(
                'relative space-y-2 overflow-hidden transition-all duration-300',
                !isExpanded && 'max-h-60'
            )">
                <div v-for="(segment, index) in segments" :key="index"
                    class="group flex gap-4 rounded-lg p-3 transition-colors hover:bg-muted/50">
                    <div class="flex flex-col items-center">
                        <Badge variant="outline" class="font-mono text-xs">
                            {{ formatTime(segment.start) }}
                        </Badge>
                        <div class="my-1 h-full w-px bg-border" />
                        <Badge variant="outline" class="font-mono text-xs">
                            {{ formatTime(segment.end) }}
                        </Badge>
                    </div>
                    <p class="flex-1 text-sm leading-relaxed">{{ segment.text }}</p>
                </div>

                <div v-if="!isExpanded && segments.length > 3"
                    class="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-card to-transparent" />
            </div>

            <Button v-if="viewMode === 'full' || segments.length > 3" variant="ghost" class="w-full"
                @click="isExpanded = !isExpanded">
                <template v-if="isExpanded">
                    <ChevronUp class="mr-2 h-4 w-4" />
                    Show Less
                </template>
                <template v-else>
                    <ChevronDown class="mr-2 h-4 w-4" />
                    Show More
                </template>
            </Button>
        </CardContent>
    </Card>
</template>