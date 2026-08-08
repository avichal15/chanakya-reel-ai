/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./*.{ts,tsx}",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./pages/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
        "./reddit/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'studio-dark': '#0b0f19',
                'studio-panel': '#151a28',
                'studio-accent': '#3b82f6',
                'reddit': '#FF4500',
            },
            fontFamily: {
                display: ['Montserrat', 'Inter', 'sans-serif'],
            },
            keyframes: {
                'fade-in': {
                    '0%': { opacity: '0', transform: 'translateY(4px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
            },
            animation: {
                'fade-in': 'fade-in 0.3s ease-out both',
            },
        },
    },
    plugins: [
        require("tailwindcss-animate"),
    ],
}
