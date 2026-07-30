<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Brain, Plus } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
</script>

<template>
    <header
        class="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div class="container mx-auto flex h-16 items-center justify-between">
            <RouterLink to="/" class="flex items-center gap-2">
                <div class="flex h-9 w-9 items-center justify-center bg-primary">
                    <Brain class="h-5 w-5 text-primary-foreground" />
                </div>
                <span class="text-xl font-bold tracking-tight">TalentLens</span>
            </RouterLink>

            <Button asChild size="lg" class="shrink-0">
                <RouterLink to="/upload">
                    <Plus class="mr-2 h-5 w-5" />
                    New Assessment
                </RouterLink>
            </Button>
        </div>
    </header>
</template>