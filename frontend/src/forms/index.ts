import Tagify from "@yaireo/tagify";
import "./styles.scss";

function initializeForms(rootEl: HTMLElement | Document) {
    for (const el of rootEl.querySelectorAll("input[type=text].tagwidget")) {
        new Tagify(el as HTMLInputElement, {
            pattern: /^[^"]+$/,
            originalInputValueFormat: (arr) =>
                arr.map((item) => `"${item.value}"`).join(","),
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initializeForms(document);
});

(window as any).gwInitializeForms = initializeForms;
