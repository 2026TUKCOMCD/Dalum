/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  important: true,
  theme: {
    extend: {
      colors: {
        primary: {
          900: "#1E3A8A",
        },
        secondary: {
          900: "#F0F5FA",
        },
        gray: {
          900: "#222222",
          800: "#444444",
          700: "#666666",
          600: "#888888",
          500: "#CCCCCC",
          100: "#E5E5E5",
          50: "#F1F2F4",
          0: "#FFFFFF",
        },
        button: {
          like: "#EA4335",
          kakao: "#FAE100",
          naver: "#03C75A",
          google: "#F2F2F2",
        },
        screen: {
          default: "#FAFAFA",
          modal: "#00000033",
        },
      },
      fontSize: {
        h1_32: ["32px", { lineHeight: "140%" }],
        h2_24: ["24px", { lineHeight: "140%" }],
        body_20: ["20px", { lineHeight: "140%" }],
        body_18: ["18px", { lineHeight: "140%" }],
        body_16: ["16px", { lineHeight: "140%" }],
        body_14: ["14px", { lineHeight: "140%" }],
        body_12: ["12px", { lineHeight: "140%" }],
        body_10: ["10px", { lineHeight: "140%" }],
      },
      backgroundImage: {
        "chevron-left": "url('/icons/chevron-left.svg')",
        "chevron-right": "url('/icons/chevron-right.svg')",
        close: "url('/icons/close.svg')",
        kakao: "url('/icons/kakao.svg')",
        naver: "url('/icons/naver.svg')",
        google: "url('/icons/google.svg')",
      },
      textColor: (theme) => ({
        ...theme("colors"),
      }),
      backgroundColor: (theme) => ({
        ...theme("colors"),
      }),
      fontFamily: {
        pretendard: [
          "Pretendard",
          "-apple-system",
          "BlinkMacSystemFont",
          "system-ui",
          "sans-serif",
        ],
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
