export interface VideoUpload {
    file: File
    question: string
    rubric: string
    preview?: string
}

export interface VideoAssessment {
    video_id: number
    file_path: string
    question: string
    final_score: number
    rubric_reason: string
    fluency_score: number
    ai_likeness_label: string
    ai_silence_score: number
    full_transcript: string
    segments: [number, number, string][] // Tuple type
    pauses: number[]
    duration_sec: number
}

export interface AssessmentReport {
    id?: string;
    generated_at: string;
    total_videos: number;
    videos: VideoAssessment[];
    candidate_name?: string;
    position?: string;
}

export const mockAssessments: AssessmentReport[] = [
    {
        id: "1",
        generated_at: "2025-12-07T05:02:21.181150",
        total_videos: 2,
        candidate_name: "Alex Johnson",
        position: "Senior Software Engineer",
        videos: [
            {
                video_id: 1,
                file_path: "interview_question_1.webm",
                question: "Can you share any specific challenges you faced while working on certification and how you overcame them?",
                final_score: 4,
                rubric_reason: "Provides detailed examples with clear problem-solving approach.",
                fluency_score: 4,
                ai_likeness_label: "Not AI-like",
                ai_silence_score: 4,
                full_transcript: "For the challenges, there were several when I took the certification. The first was dealing with validation loss and accuracy. I experimented with different architectures, adding more layers, neurons, and dropout layers. This really helped reduce the validation loss significantly.",
                segments: [
                    [0, 15, "For the challenges, there were several when I took the certification."],
                    [15, 35, "The first was dealing with validation loss and accuracy."],
                    [35, 55, "I experimented with different architectures, adding more layers, neurons, and dropout layers."],
                    [55, 70, "This really helped reduce the validation loss significantly."]
                ],
                pauses: [1],
                duration_sec: 70
            },
            {
                video_id: 2,
                file_path: "interview_question_2.webm",
                question: "Describe a time when you had to work with a difficult team member.",
                final_score: 3,
                rubric_reason: "Good structure but lacks specific outcomes.",
                fluency_score: 3,
                ai_likeness_label: "Somewhat AI-like",
                ai_silence_score: 3,
                full_transcript: "I once worked with a colleague who had different communication styles. We scheduled regular one-on-ones to align our expectations and improve collaboration.",
                segments: [
                    [0, 20, "I once worked with a colleague who had different communication styles."],
                    [20, 45, "We scheduled regular one-on-ones to align our expectations and improve collaboration."]
                ],
                pauses: [2],
                duration_sec: 45
            }
        ]
    },
    {
        id: "2",
        generated_at: "2025-12-06T14:30:00.000000",
        total_videos: 1,
        candidate_name: "Maria Garcia",
        position: "Product Manager",
        videos: [
            {
                video_id: 1,
                file_path: "pm_interview.webm",
                question: "How do you prioritize features in a product roadmap?",
                final_score: 5,
                rubric_reason: "Excellent framework-based approach with clear metrics.",
                fluency_score: 5,
                ai_likeness_label: "Not AI-like",
                ai_silence_score: 5,
                full_transcript: "I use a combination of RICE scoring and customer feedback analysis. First, I gather data from user interviews and analytics. Then I score each feature based on reach, impact, confidence, and effort. This gives us a prioritized list that balances business value with user needs.",
                segments: [
                    [0, 15, "I use a combination of RICE scoring and customer feedback analysis."],
                    [15, 30, "First, I gather data from user interviews and analytics."],
                    [30, 50, "Then I score each feature based on reach, impact, confidence, and effort."],
                    [50, 65, "This gives us a prioritized list that balances business value with user needs."]
                ],
                pauses: [],
                duration_sec: 65
            }
        ]
    }
];

export const getAssessmentById = (id: string) => mockAssessments.find(a => a.id === id);