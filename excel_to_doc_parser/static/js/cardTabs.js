"use strict";

const tabs = document.querySelectorAll(".card-module__title");


tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        if (tab.nextElementSibling.classList.contains("d-flex")) {
            tab.nextElementSibling.classList.remove("d-flex");
        } else tab.nextElementSibling.classList.add("d-flex");
    })
}) 