document.addEventListener('DOMContentLoaded', () => {

    const filter = document.querySelector('.material-symbols-outlined');
    const filterList = document.querySelector('.filter_list');

    filter.addEventListener('click', toggleFilterList);

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


function redirectToUrl(element) {
    var url = element.dataset.url;
    window.location.href = url;
}