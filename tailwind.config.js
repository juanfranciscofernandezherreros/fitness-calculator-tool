/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  theme: {
    extend: {
      colors: {
        marca: {
          dark:   "#1B263B", // Azul oscuro
          light:  "#F0F4F8", // Blanco hielo
          accent: "#415A77", // Azul acero
        },
      },
    },
  },
  plugins: [],
};
