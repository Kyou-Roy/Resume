document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("inventorySearch");

    const statusFilter =
        document.getElementById("statusFilter");

    const table =
        document.getElementById("inventoryTable");

    const resultCount =
        document.getElementById("resultCount");


    if (!table) {
        return;
    }


    const rows =
        table.querySelectorAll("tbody tr");


    function filterInventory() {

        const keyword =
            searchInput.value
                .toLowerCase()
                .trim();

        const selectedStatus =
            statusFilter.value;

        let visibleCount = 0;


        rows.forEach(function (row) {

            const rowText =
                row.innerText.toLowerCase();

            const statusCell =
                row.cells[5].innerText.trim();

            const keywordMatch =
                rowText.includes(keyword);

            const statusMatch =
                selectedStatus === "all"
                || statusCell.includes(selectedStatus);


            if (keywordMatch && statusMatch) {

                row.style.display = "";
                visibleCount++;

            } else {

                row.style.display = "none";

            }

        });


        resultCount.textContent =
            "\uAC80\uC0C9 \uACB0\uACFC: "
            + visibleCount
            + "\uAC74";
    }


    searchInput.addEventListener(
        "input",
        filterInventory
    );


    statusFilter.addEventListener(
        "change",
        filterInventory
    );


    filterInventory();

});