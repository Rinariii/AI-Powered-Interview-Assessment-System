<script setup lang="ts">
import { Card, CardContent } from "@/components/ui/card"
import type { LucideIcon } from "lucide-vue-next";

interface Props {
    title: string;
    value: string | number;
    description?: string;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    class?: string;
}

defineProps<Props>();
</script>

<template>
    <Card class="relative overflow-hidden">
        <CardContent class="p-6">
            <div class="flex items-start justify-between">
                <div class="space-y-2">
                    <p class="text-sm font-medium text-muted-foreground">{{ title }}</p>
                    <p class="text-3xl font-bold tracking-tight">{{ value }}</p>
                    <p v-if="description" class="text-xs text-muted-foreground">{{ description }}</p>

                    <p v-if="trend" :class="[
                        'text-xs font-medium',
                        trend.isPositive ? 'text-green-600' : 'text-red-600'
                    ]">
                        {{ trend.isPositive ? "+" : "" }}{{ trend.value }}% from last month
                    </p>
                </div>
                <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <component :is="icon" class="h-6 w-6 text-primary" />
                </div>
            </div>
        </CardContent>
    </Card>
</template>