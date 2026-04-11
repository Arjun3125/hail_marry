"use client";

import { useEffect } from "react";

export function LowDataAssetController() {
    useEffect(() => {
        const prepareImages = () => {
            if (!document.documentElement.classList.contains("low-data-mode")) return;
            document.querySelectorAll("img").forEach((image) => {
                image.setAttribute("loading", "lazy");
                image.setAttribute("data-low-data-loaded", image.getAttribute("data-low-data-loaded") || "false");
                image.setAttribute("title", image.getAttribute("title") || "Low-data mode: tap to reveal image");
            });
        };

        const handleClick = (event: MouseEvent) => {
            const target = event.target;
            if (!(target instanceof HTMLImageElement)) return;
            if (!document.documentElement.classList.contains("low-data-mode")) return;
            target.setAttribute("data-low-data-loaded", "true");
        };

        prepareImages();
        document.addEventListener("click", handleClick, true);
        const observer = new MutationObserver(prepareImages);
        observer.observe(document.body, { childList: true, subtree: true });
        return () => {
            document.removeEventListener("click", handleClick, true);
            observer.disconnect();
        };
    }, []);

    return null;
}
