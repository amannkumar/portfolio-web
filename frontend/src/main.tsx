import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import Clarity from "@microsoft/clarity";

Clarity.init("vtbi00udwj");

createRoot(document.getElementById("root")!).render(<App />);
