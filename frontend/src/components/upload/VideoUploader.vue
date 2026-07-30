<script setup lang="ts">
import { ref } from 'vue'
import { Upload, X, FileVideo, Trash2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { cn } from '@/lib/utils'

// Components
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

import type { VideoUpload } from '@/types/assessment'

// Props & Emits
defineProps<{
    isLoading?: boolean
}>()

const emit = defineEmits<{
    (e: 'submit', files: VideoUpload[]): void
}>()

// State
const videos = ref<VideoUpload[]>([])
const isDragging = ref(false)

// Actions
const processFiles = (fileList: FileList | File[]) => {
    const files = Array.from(fileList).filter(file =>
        file.type.startsWith('video/')
    )

    if (files.length === 0 && fileList.length > 0) {
        toast({
            title: "Invalid file type",
            description: "Please upload video files only (.mp4, .webm, etc.)",
            variant: "destructive"
        })
        return
    }

    const newVideos: VideoUpload[] = files.map(file => ({
        file,
        question: "",
        rubric: "",
        preview: URL.createObjectURL(file)
    }))

    videos.value = [...videos.value, ...newVideos]
}

const handleDrop = (e: DragEvent) => {
    isDragging.value = false
    if (e.dataTransfer?.files) {
        processFiles(e.dataTransfer.files)
    }
}

const handleFileSelect = (e: Event) => {
    const input = e.target as HTMLInputElement
    if (input.files) {
        processFiles(input.files)
        // Reset input so selecting the same file again works if needed
        input.value = ''
    }
}

const removeVideo = (index: number) => {
    const video = videos.value[index]
    if (!video) return
    if (video.preview) {
        URL.revokeObjectURL(video.preview)
    }
    videos.value.splice(index, 1)
}

const clearAll = () => {
    videos.value.forEach(v => {
        if (v.preview) URL.revokeObjectURL(v.preview)
    })
    videos.value = []
}

const handleSubmit = () => {
    const incomplete = videos.value.some(v => !v.question.trim() || !v.rubric.trim())

    if (incomplete) {
        toast({
            title: "Missing information",
            description: "Please provide a question and rubric for each video.",
            variant: "destructive"
        })
        return
    }

    emit('submit', videos.value)
}
</script>

<template>
    <div class="space-y-6">
        <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
            :class="cn(
                'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all duration-200',
                isDragging
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50 hover:bg-muted/50'
            )">
            <input type="file" accept="video/*" multiple class="absolute inset-0 cursor-pointer opacity-0"
                @change="handleFileSelect" />
            <div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <Upload class="h-8 w-8 text-primary" />
            </div>
            <h3 class="mt-4 text-lg font-semibold">Upload Interview Videos</h3>
            <p class="mt-2 text-sm text-muted-foreground text-center">
                Drag and drop video files here, or click to browse
            </p>
            <p class="mt-1 text-xs text-muted-foreground">
                Supports MP4, WebM, and other video formats
            </p>
        </div>

        <div v-if="videos.length > 0" class="space-y-4">
            <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold">
                    Videos to Analyze ({{ videos.length }})
                </h3>
                <Button variant="outline" size="sm" class="text-destructive hover:text-destructive" @click="clearAll">
                    <Trash2 class="mr-2 h-4 w-4" />
                    Clear All
                </Button>
            </div>

            <div class="grid gap-4">
                <Card v-for="(video, index) in videos" :key="index" class="relative">
                    <Button variant="ghost" size="icon"
                        class="absolute right-2 top-2 h-8 w-8 text-muted-foreground hover:text-destructive"
                        @click="removeVideo(index)">
                        <X class="h-4 w-4" />
                    </Button>

                    <CardContent class="p-6">
                        <div class="grid gap-6 md:grid-cols-[200px_1fr]">
                            <div class="space-y-2">
                                <div class="aspect-video overflow-hidden rounded-lg bg-muted">
                                    <video v-if="video.preview" :src="video.preview" class="h-full w-full object-cover"
                                        controls />
                                    <div v-else class="flex h-full items-center justify-center">
                                        <FileVideo class="h-12 w-12 text-muted-foreground" />
                                    </div>
                                </div>
                                <p class="text-xs text-muted-foreground truncate">
                                    {{ video.file.name }}
                                </p>
                            </div>

                            <div class="space-y-4">
                                <div class="space-y-2">
                                    <Label :for="`question-${index}`">
                                        Interview Question
                                    </Label>
                                    <Input :id="`question-${index}`"
                                        placeholder="e.g., Can you describe a challenging project you've worked on?"
                                        v-model="video.question" />
                                </div>
                                <div class="space-y-2">
                                    <Label :for="`rubric-${index}`">
                                        Evaluation Rubric
                                    </Label>
                                    <Textarea :id="`rubric-${index}`"
                                        placeholder="e.g., Provides specific examples with clear problem-solving approach and measurable outcomes."
                                        v-model="video.rubric" :rows="3" />
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Button class="w-full" size="lg" :disabled="isLoading || videos.length === 0" @click="handleSubmit">
                <template v-if="isLoading">
                    <div class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Analyzing Videos...
                </template>
                <template v-else>
                    Analyze {{ videos.length }} Video{{ videos.length > 1 ? "s" : "" }}
                </template>
            </Button>
        </div>
    </div>
</template>