<script>
	export let html_rows;
	export let columns;
	/**
	 * @type {{ style: { backgroundColor: string; }; }}
	 */
	var _el;
	/**
	 * @type {any}
	 */
	var oldStyle;

	/**
	 * @param {{ style?: { backgroundColor: string; }; parentNode?: any; previousSibling?: any; }} el1
	 * @param {{ parentNode: any; }} el2
	 */
	function isBefore(el1, el2) {
		if (el2.parentNode === el1.parentNode)
			for (var cur = el1.previousSibling; cur && cur.nodeType !== 9; cur = cur.previousSibling)
				if (cur === el2) return true;
		return false;
	}

	/**
	 * @type {import("svelte/elements").DragEventHandler<HTMLDivElement>}
	 */
	function dragStart(e) {
		console.log('dragStart()');
		e.dataTransfer.effectAllowed = 'move';
		e.dataTransfer.setData('text/plain', null);
		_el = e.target;
		oldStyle = _el.style.backgroundColor;
		_el.style.backgroundColor = '#e5e5e5';
	}

	/**
	 * @type {import("svelte/elements").DragEventHandler<HTMLDivElement>}
	 */
	function dragOver(e) {
		// console.log('dragOver()');
		if (isBefore(_el, e.target.parentNode)) {
			e.target.parentNode.parentNode.insertBefore(_el, e.target.parentNode);
		} else {
			e.target.parentNode.parentNode.insertBefore(_el, e.target.parentNode.nextSibling);
		}
	}

	/**
	 * @param {any} e
	 */
	function dragEnd(e) {
		// console.log('dragEnd()');
		console.log(e);
		_el.style = oldStyle;
	}

	/**
	 * @param {{ preventDefault: () => void; touches: string | any[]; targetTouches: { target: { style: { backgroundColor: string; }; }; }[]; }} e
	 */
	function touchStart(e) {
		console.log('touchStart()');
		e.preventDefault();

		if (e.touches.length == 1) {
			_el = e.targetTouches[0].target;
			oldStyle = _el.style.backgroundColor;
			_el.style.backgroundColor = '#e5e5e5';
		}
	}

	/**
	 * @param {{ preventDefault: () => void; target: { parentNode: any; nextSibling?: any; }; }} e
	 */
	function touchMove(e) {
		console.log('touchMove()');
		e.preventDefault();

		if (isBefore(_el, e.target)) e.target.parentNode.insertBefore(_el, e.target);
		else e.target.parentNode.insertBefore(_el, e.target.nextSibling);
	}

	/**
	 * @param {any} e
	 */
	function touchEnd(e) {
		console.log('touchEnd()');
		_el.style = oldStyle;
	}
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
</svelte:head>

<!-- <div style="list-style-type:none;font-size: 18pt; font-weight:bold;">
	{#each list as item}
		<div
			class="item"
			draggable="true"
			on:dragstart={dragStart}
			on:dragover={dragOver}
			on:dragend={dragEnd}
			on:touchstart={touchStart}
			on:touchmove={touchMove}
			on:touchend={touchEnd}
		>
			{item}
		</div>
	{/each}
</div> -->

<div style="list-style-type:none;font-size: 18pt; font-weight:bold;">
	<table>
		<thead>
			<tr>
				{#each columns as col}
					<td>{col}</td>
				{/each}
			</tr>
		</thead>

		<tbody>
			{#each html_rows as row}
				<tr
					class="item"
					draggable="true"
					on:dragstart={dragStart}
					on:dragover={dragOver}
					on:dragend={dragEnd}
					on:touchstart={touchStart}
					on:touchmove={touchMove}
					on:touchend={touchEnd}
				>
					{#each row as cell}
						<td>{' ' + cell + ' '}</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.item {
		user-select: none;
		width: 200px;
		border-style: solid;
		border-width: 1px;
		border-color: gray;
		padding: 10px;
		text-align: center;
	}
	table thead td {
		text-align: left;
		writing-mode: sideways-lr;
	}
	table tbody td {
		min-width: 20px;
		border: 1px solid gray;
		padding: 0.2em;
		margin: 0;
	}
	table {
		border-collapse: collapse;
	}
</style>
