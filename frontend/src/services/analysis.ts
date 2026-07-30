import type { VideoUpload, AssessmentReport } from '@/types/assessment';

const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
    throw new Error('VITE_API_URL must be configured in frontend/.env');
}

export const analyzeVideos = async (videos: VideoUpload[]): Promise<AssessmentReport> => {
    const formData = new FormData();

    const questions: string[] = [];
    const rubrics: string[] = [];

    videos.forEach((video) => {
        formData.append('files', video.file);
        questions.push(video.question);
        rubrics.push(video.rubric);
    });

    const metadata = {
        questions,
        rubrics
    };

    formData.append('metadata', JSON.stringify(metadata));

    const response = await fetch(`${apiUrl.replace(/\/$/, '')}/analyze`, {
        method: 'POST',
        headers: {
            'accept': 'application/json',
        },
        body: formData
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Analysis failed: ${response.status} ${response.statusText} - ${errorText}`);
    }

    return await response.json();
};
