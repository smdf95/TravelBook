
document.addEventListener('DOMContentLoaded', () => {

    const filter = document.querySelector('.material-symbols-outlined.filter');
    const filterList = document.querySelector('.filter_list');

    if (filter && filterList) {
        filter.addEventListener('click', toggleFilterList);
    }

    function toggleFilterList() {
        // Check if filterList is currently visible
        if (filterList.style.display === "block") {
            // If visible, hide it
            filterList.style.display = "none";
        } else {
            // If hidden, show it
            filterList.style.display = "block";
        }
    }
})

// document.addEventListener('DOMContentLoaded', () => {
//     const commentButton = document.querySelector('.comment-button');
//     const commentForm = document.querySelector('.comment-form');

//     if (commentButton && commentForm) {
//         commentButton.addEventListener('click', toggleCommentForm);
//     }

//     function toggleCommentForm(event) {
//         event.preventDefault(); // Prevent the default behavior of the link

//         // Toggle the visibility of the comment form
//         if (commentForm.style.display === "block") {
//             commentForm.style.display = "none";
//         } else {
//             commentForm.style.display = "block";
//         }
//     }
// });


function redirectToUrl(element) {
    var url = element.dataset.url;
    window.location.href = url;
}

function changeIcon(element, iconName) {
    const iconElement = element.querySelector('.material-icons');
    if (iconElement) {
        iconElement.textContent = iconName;
    }
}
