/** @type {import('tailwindcss').Config} */
// 수정 예정
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  important: true,
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#9FD416",
          40: "#A9E119",
          30: "#D1F27D",
          20: "#E3FBA6",
          10: "#F1FFCE",
        },
        gray: {
          900: "#1A1E22",
          800: "#33373B",
          700: "#4C5054",
          600: "#65696D",
          500: "#7E8286",
          400: "#979B9F",
          300: "#B0B4B8",
          200: "#C9CDD1",
          100: "#E9ECEF",
          50: "#F2F4F6",
        },
        screen: {
          0: "#FCFDFF",
        },
        alert: {
          50: "#E84A4A",
        },
      },
      fontSize: {
        h1_24: ["24px", { lineHeight: "140%" }],
        h2_20: ["20px", { lineHeight: "140%" }],
        body_18: ["18px", { lineHeight: "140%" }],
        body_16: ["16px", { lineHeight: "140%" }],
        body_14: ["14px", { lineHeight: "140%" }],
        body_12: ["12px", { lineHeight: "140%" }],
      },
      textColor: (theme) => ({
        ...theme("colors"),
      }),
      backgroundColor: (theme) => ({
        ...theme("colors"),
      }),
      fontFamily: {
        suite: ["SUITE Variable", "SUITE", "system-ui", "sans-serif"],
      },
      borderColor: (theme) => ({
        ...theme("colors"),
      }),
      boxShadow: {},
      backgroundImage: {},
    },
  },
  plugins: [],
};
