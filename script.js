function truncateFunction(){
    const collection = document.getElementsByClassName("truncate");
    Array.from(collection).forEach((element)=>{
        let numberOfWords=element.getAttribute("data-length");
        if(numberOfWords==0){
            return;
        }
        let currentWidth=window.innerWidth;
        if(currentWidth<1400){
            let difference=1400-currentWidth;
            numberOfWords-=difference/100;
            if(numberOfWords<15){
                numberOfWords=15;
            }
        }

        let firstWords=element.innerHTML.split(' ').slice(0,numberOfWords).join(' ')+" ..."
        let smallParagraph=document.createElement("p");
        smallParagraph.classList.add("truncate");
        smallParagraph.innerHTML=firstWords;
        element.classList.toggle("hidden");
        insertAfter(smallParagraph,element);
    })
    addEvent();
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
    }
    else if(text=="Read Less"){
        const parent=button.parentNode;
        button.innerHTML="Read More "+chevron;
        let bigParagraph=parent.children.item(0);
        let smallParagraph=parent.children.item(1);
        bigParagraph.classList.toggle("hidden");
        smallParagraph.classList.toggle("hidden");
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
            if(index>1){
                item.classList.toggle("hidden",true);
            }

        })

    }

}

function addEvent(){
    document.querySelector("#hamburger").addEventListener('click',(element)=>{
        document.querySelector('.secondary-menu').classList.toggle("toggle")
    })
}

document.addEventListener("scroll",()=>{
    document.querySelector('.secondary-menu').classList.toggle("toggle",false);
})

window.onresize = function() {
    if(window.innerWidth>900){
        document.querySelector(".secondary-menu").classList.toggle("toggle",false);
    }
}