/** @type {import('tailwind').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#09090b', // Deep sentinel black
                card: '#18181b',       // lighter black for cards
                border: '#27272a',     // border color
                brand: {
                    green: '#10b981',    // Approve
                    yellow: '#f59e0b',   // Review
                    red: '#ef4444',
                }
            }
        },
    },
    plugins: [],
}