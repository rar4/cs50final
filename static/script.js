function endBrainstorm(document)
{
    window.location.replace(`/idea?title=${encodeURIComponent(document.querySelector("p").innerHTML)}&img=${encodeURIComponent(document.getElementById("img").src)}`);
}

