"use strict";

let darkTheme = localStorage.getItem("darkTheme");
const darkThemeToggle = document.querySelector(".main-btn__container"),
    btns = document.querySelectorAll(".main__btn"),
    body = document.querySelector("body"),
    appName = document.querySelector(".header__title"),
    title = document.querySelector(".main__title"),
    main = document.querySelector(".main"),
    text = document.querySelector(".main__changetheme");


if (darkTheme === "enabled") {
    enableDarkMode();
    darkThemeToggle.checked = localStorage.getItem("darkTheme");
};

darkThemeToggle.addEventListener("click", () => {
    darkTheme = localStorage.getItem("darkTheme");
    if (darkTheme !== "enabled") {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
});


// Functions 

function enableDarkMode() {
    btns.forEach((btn) => {
        btn.classList.add("dark-btn");
    });

    body.classList.add("bg-black");
    title.classList.add("white-color");
    appName.classList.add("white-color");
    main.classList.add("main-styles");
    darkThemeToggle.classList.add("border-white");
    text.classList.add("white-color");

    localStorage.setItem("darkTheme", "enabled");
};

function disableDarkMode() {

    btns.forEach((btn) => {
        btn.classList.remove("dark-btn");
    });

    body.classList.remove("bg-black");
    title.classList.remove("white-color");
    appName.classList.remove("white-color");
    main.classList.remove("main-styles");
    darkThemeToggle.classList.remove("border-white");
    text.classList.remove("white-color");

    localStorage.setItem("darkTheme", null);
};


