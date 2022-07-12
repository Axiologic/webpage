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
        const parent=button.parentNode;
        button.innerHTML="Read Less "+chevron;
        let bigParagraph=parent.children.item(0);
        let smallParagraph=parent.children.item(1);
        bigParagraph.classList.toggle("hidden");
        smallParagraph.classList.toggle("hidden");
        if(parent.className=="project-description")
        {
            parent.style.maxWidth="830px";
        }

    }
    else if(text=="Read Less"){
        const parent=button.parentNode;
        button.innerHTML="Read More "+chevron;
        let bigParagraph=parent.children.item(0);
        let smallParagraph=parent.children.item(1);
        bigParagraph.classList.toggle("hidden");
        smallParagraph.classList.toggle("hidden");
        if(parent.className=="project-description")
        {
            parent.style.maxWidth="537px";
        }
    }
}

function viewMoreItems(className,name){
    let button=event.target;
    const items=Array.from(document.getElementsByClassName(className));
    if(button.innerHTML.includes("View All")){
        button.innerHTML="Show Less"
        items.forEach((item)=>{
            item.classList.toggle("hidden",false);
        })
    }
    else
    {
        button.innerHTML="View All "+name;
        items.forEach((item,index)=>{
            if(index>2){
                item.classList.toggle("hidden",true);
            }

        })

    }

}

