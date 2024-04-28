<script>
	/** @type {import('./$types').PageData} */
	export let data;

    /**
	 * @type {any[]}
	 */
    let columns = data.table[0]

    /**
	 * @type {any[]}
	 */
     let html_rows = data.table.slice(1)
</script>


<div class="w3-row-padding w3-margin-bottom">
    <div class="w3-col s12">

<table>
    
    <thead>
        <tr>
            {#each columns as col}
                <td style="text-align: left; writing-mode: sideways-lr">{col}</td>
            {/each}
        </tr>
    </thead>

    <tbody>
        {#each html_rows as row}
          <tr>
            {#each row as cell}
              <td style="min-width:20px;border:1px solid gray">{" " + cell + " "}</td>
            {/each}
          </tr>
        {/each}
    </tbody>

</table>

</div>
</div>