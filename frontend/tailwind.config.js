/** @type {import('tailwind').Config} */
export default {
    xontent: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#09090b', // Deep sentinel black (zinc-950)
                card: '#18181b',       // Slightly lighter black for cards
                border: '#27272a',     // Subtle border color
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