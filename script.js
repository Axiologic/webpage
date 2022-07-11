function truncateFunction(){
    const collection = document.getElementsByClassName("truncate");
    Array.from(collection).forEach((element)=>{
        let numberOfWords=element.className.split(" ")[1];
        let firstWords=element.innerHTML.split(' ').slice(0,numberOfWords).join(' ')+" ..."
        let smallParagraph=document.createElement("p");
        smallParagraph.classList.add("truncate");
        smallParagraph.innerHTML=firstWords;
        element.classList.toggle("hidden");
        insertAfter(smallParagraph,element);


    })
}

function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

function readMore(button){
    const chevron="<i class=\"fa-solid fa-chevron-down \"></i>"
    let text=button.innerHTML.split(" ").slice(0,2).join(" ");
    if(text=="Read More"){
        const parent=button.parentNode.children;
        button.innerHTML="Read Less "+chevron;
        let bigParagraph=parent.item(0);
        let smallParagraph=parent.item(1);
        bigParagraph.classList.toggle("hidden",false);
        smallParagraph.classList.toggle("hidden");
    }
    else if(text=="Read Less"){
        const parent=button.parentNode.children;
        button.innerHTML="Read More "+chevron;
        let bigParagraph=parent.item(0);
        let smallParagraph=parent.item(1);

        bigParagraph.classList.toggle("hidden");
        smallParagraph.classList.toggle("hidden");
    }


}