<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

interface Props {
    score: number
    maxScore?: number
    label: string
    size?: 'sm' | 'md' | 'lg'
    showPercentage?: boolean
}

// Define props with default values
const props = withDefaults(defineProps<Props>(), {
    maxScore: 5,
    size: 'md',
    showPercentage: false
})

// Constants
const radius = 45
const circumference = 2 * Math.PI * radius

// Configuration Maps
const sizeClasses = {
    sm: "h-20 w-20",
    md: "h-28 w-28",
    lg: "h-36 w-36"
}

const textSizeClasses = {
    sm: "text-lg",
    md: "text-2xl",
    lg: "text-3xl"
}

// Computed Logic
const percentage = computed(() => (props.score / props.maxScore) * 100)

const strokeDashoffset = computed(() => {
    return circumference - (percentage.value / 100) * circumference
})

const scoreColorClass = computed(() => {
    const pct = percentage.value
    if (pct >= 80) return "stroke-green-500"
    if (pct >= 60) return "stroke-yellow-500"
    if (pct >= 40) return "stroke-orange-500"
    return "stroke-red-500"
})
</script>

<template>
    <div class="flex flex-col items-center gap-2">
        <div :class="cn('relative', sizeClasses[props.size])">
            <svg class="h-full w-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" :r="radius" fill="none" stroke="currentColor" stroke-width="8"
                    class="text-muted/30" />
                <circle cx="50" cy="50" :r="radius" fill="none" stroke-width="8" stroke-linecap="round"
                    :class="cn('transition-all duration-1000 ease-out', scoreColorClass)" :style="{
                        strokeDasharray: circumference,
                        strokeDashoffset: strokeDashoffset
                    }" />
            </svg>

            <div class="absolute inset-0 flex items-center justify-center">
                <span :class="cn('font-bold', textSizeClasses[props.size])">
                    {{ showPercentage ? `${Math.round(percentage)}%` : score }}
                </span>
            </div>
        </div>

        <span class="text-sm font-medium text-muted-foreground text-center">
            {{ label }}
        </span>
    </div>
</template>