<script>
	import { quintOut } from 'svelte/easing';
	import { crossfade } from 'svelte/transition';
	import { flip } from 'svelte/animate';

	export let data;

	let races = data.races;
	let foundersDay = data.foundersDay;

	let tuples = [...foundersDay];

	for (const [uid, race] of Object.entries(races)) {
		if (race.heats === undefined) {
			console.log({ race });
			continue;
		}
		for (const heat of race.heats) {
			if (heat.class === 'fours' && heat.gender === 'girls' && heat.varsity_index === '1') {
				for (let i = 0; i < heat.results.length - 1; i++) {
					for (let j = i + 1; j < heat.results.length; j++) {
						tuples.push([
							heat.results[i].school,
							heat.results[j].school,
							Math.round(
								100 * (heat.results[j].margin_from_winner - heat.results[i].margin_from_winner)
							) / 100,
							race.day
						]);
					}
				}
			}
		}
	}

	tuples.sort((a, b) => {
		a = a[3];
		b = b[3];
		return -(a < b ? -1 : a > b ? 1 : 0);
	});

	const [send, receive] = crossfade({
		duration: (d) => Math.sqrt(d * 200),

		fallback(node, params) {
			const style = getComputedStyle(node);
			const transform = style.transform === 'none' ? '' : style.transform;

			return {
				duration: 600,
				easing: quintOut,
				css: (t) => `
					transform: ${transform} scale(${t});
					opacity: ${t}
				`
			};
		}
	});

	let uid = 1;

	let schools = [
		'Nobles',
		'Groton',
		'Brooks',
		'BB&N',
		'Middlesex',
		'Taft',
		'Cambridge RLS',
		'Choate',
		'Hopkins',
		'Winsor',
		'Frederick Gunn',
		"Miss Porter's",
		'Brewster Academy',
		'Canterbury',
		'Greenwich Academy',
		'Lyme/Old Lyme',
		"St. Mark's",
		'NMH',
		'Berkshire Academy',
		'Newton Country Day',
		'Pomfret'
	];

	let unseeded = schools.map((school) => ({
		id: uid++,
		description: school
	}));

	let seeding = [];

	let selected = [unseeded[0]];

	function add(input) {
		const todo = {
			id: uid++,
			done: false,
			seeded: false,
			description: input.value
		};

		todos = [todo, ...todos];
		input.value = '';
	}

	function moveUp(list, index) {
		if (index <= 0) return list;
		if (list === undefined) console.error('wat');
		return [...list.slice(0, index - 1), selected[0], list[index - 1], ...list.slice(index + 1)];
	}

	function moveDown(list, index) {
		if (index >= list.length - 1) return list;
		return [...list.slice(0, index), list[index + 1], selected[0], ...list.slice(index + 2)];
	}

	function remove(todo) {
		todos = todos.filter((t) => t !== todo);
	}

	function moveToSeeding(x) {
		console.log('moveToSeeding(' + JSON.stringify(x) + ')');
		let newValue = { ...selected[0], seeded: true };
		let index = unseeded.map((x) => x.id).indexOf(newValue.id);
		seeding = [...seeding.slice(0, index), newValue, ...seeding.slice(index)];
		unseeded = unseeded.filter((x) => x.id != newValue.id);
		selected = [newValue];
	}

	function moveToUnseeded(x) {
		console.log('moveToUnseeded(' + JSON.stringify(x) + ')');
		let newValue = { ...selected[0], seeded: false };
		let index = seeding.map((x) => x.id).indexOf(newValue.id);
		unseeded = [...unseeded.slice(0, index), newValue, ...unseeded.slice(index)];
		seeding = seeding.filter((x) => x.id != newValue.id);
		selected = [newValue];
	}

	// function mark(todo, done) {
	// 	todo.done = done;
	// 	remove(todo);
	// 	todos = todos.concat(todo);
	// }

	function mark(todo, seeded) {
		todo.seeded = seeded;
		remove(todo);
		todos = todos.concat(todo);
	}

	function onKeyDown(e) {
		if (![38, 40, 37, 39].includes(e.keyCode)) {
			console.log(e.keyCode);
			return;
		}

		e.preventDefault();
		if (e.repeat) return;
		if (selected.length != 1) return;

		let index = unseeded.map((x) => x.id).indexOf(selected[0].id);
		if (index < 0) {
			index = seeding.map((x) => x.id).indexOf(selected[0].id);
			switch (e.keyCode) {
				case 38: // up = 38
					seeding = moveUp(seeding, index);

					break;
				case 40: // down = 40
					seeding = moveDown(seeding, index);
					break;
				case 37: // left = 37
					moveToUnseeded(selected[0]);

					break;
				case 39: // right = 39
					// moveToSeeding(selected[0]);
					break;
			}
		} else {
			switch (e.keyCode) {
				case 38: // up = 38
					unseeded = moveUp(unseeded, index);

					break;
				case 40: // down = 40
					unseeded = moveDown(unseeded, index);
					break;
				case 37: // left = 37
					// moveToUnseeded(selected[0]);

					break;
				case 39: // right = 39
					moveToSeeding(selected[0]);
					break;
			}
		}
	}
</script>

<!-- <h1>Yo</h1> -->
<div class="w3-row-padding w3-margin-bottom toplevel" style="height: 90vh; overflow: hidden">
	<div class="w3-col s4" style="justify-content: left">
		<div class="board">
			<div class="left">
				<h2>Unseeded</h2>
				<div style="height: 100%; overflow-y: scroll">
					{#each unseeded as todo (todo.id)}
						<div
							class={'item' +
								(selected && selected[0].id == todo.id ? ' selected' : '') +
								(selected.length > 1 && selected[1].id == todo.id ? ' secondaryselect' : '')}
							in:receive={{ key: todo.id }}
							out:send={{ key: todo.id }}
							animate:flip
							on:click={(e) => {
								if (e.shiftKey) {
									selected = [selected[0], todo];
								} else {
									selected = [todo];
								}
							}}
						>
							<!-- <input type="checkbox" on:change={() => mark(todo, true)} /> -->
							{todo.description}
							<!-- <button on:click={() => remove(todo)}>remove</button> -->
						</div>
					{/each}
				</div>
			</div>

			<div class="right">
				<h2>Seeding</h2>
				{#each seeding as todo (todo.id)}
					<div
						class={'item' +
							(selected && selected[0].id == todo.id ? ' selected' : '') +
							(selected.length > 1 && selected[1].id == todo.id ? ' secondaryselect' : '')}
						in:receive={{ key: todo.id }}
						out:send={{ key: todo.id }}
						animate:flip
						on:click={(e) => {
							if (e.shiftKey) {
								selected = [selected[0], todo];
							} else {
								selected = [todo];
							}
						}}
					>
						<!-- <input type="checkbox" on:change={() => mark(todo, true)} /> -->
						{todo.description}
						<!-- <button on:click={() => remove(todo)}>remove</button> -->
					</div>
				{/each}
			</div>
		</div>
	</div>
	<div class="w3-col s8">
		<div class="selectionpane">
			{#if selected.length == 0}
				<p style="color:gray"><i>No schools have been selected</i></p>
			{/if}
			{#if selected.length == 1}
				<h2>{selected[0].description}</h2>
			{/if}
			{#if selected.length == 2}
				<h2>{selected[0].description} vs {selected[1].description}</h2>
			{/if}
		</div>
		<div class="researchpane">
			<input placeholder="filter" on:keydown={(e) => e.key === 'Enter' && add(e.target)} />
			<div class="researchtable" style="height:90%">
				<table style="border-collapse:collapse">
					<thead>
						<tr class="headerrow">
							<td>Faster School</td>
							<td>Slower School</td>
							<td>Margin</td>
							<td>Date</td>
						</tr>
					</thead>
					<tbody>
						{#each tuples as tuple}
							<tr>
								{#each tuple as cell}
									<td>{cell}</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<svelte:window on:keydown={onKeyDown} />

<style>
	.seeding {
		/* border: solid red 1px; */
	}
	.seeding div {
		border: solid green 1px;
	}
	/* .item {
		user-select: none;
		width: 200px;
		border-style: solid;
		border-width: 1px;
		border-color: gray;
		padding: 10px;
		text-align: center;
	} */

	.board {
		display: grid;
		grid-template-columns: 1fr 1fr;
		grid-gap: 1em;
		max-width: 36em;
		/* margin: 0 auto; */
		/* border: 1px solid red; */
		border-right: 1px solid gray;
		overflow-y: scroll;
	}

	.board > input {
		font-size: 1.4em;
		grid-column: 1/3;
	}

	h2 {
		font-size: 2em;
		font-weight: 200;
		user-select: none;
		margin: 0 0 0.5em 0;
	}

	.item {
		display: block;
		position: relative;
		line-height: 1.2;
		padding: 0.5em 2.5em 0.5em 1em;
		margin: 0 0 0.5em 0;
		border-radius: 2px;
		user-select: none;
		border: 1px solid hsl(240, 8%, 70%);
		background-color: hsl(240, 8%, 93%);
		color: #333;
	}

	.item:hover {
		background-color: hsl(240, 50%, 93%);
	}

	.item.selected {
		background-color: hsl(240, 100%, 93%);
	}

	.item.secondaryselect {
		background-color: hsl(240, 100%, 93%);
	}

	input[type='checkbox'] {
		position: absolute;
		left: 0.5em;
		top: 0.6em;
		margin: 0;
	}

	.done {
		border: 1px solid hsl(240, 8%, 90%);
		background-color: hsl(240, 8%, 98%);
	}

	button {
		position: absolute;
		top: 0;
		right: 0.2em;
		width: 2em;
		height: 100%;
		background: no-repeat 50% 50%
			url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23676778' d='M12,2C17.53,2 22,6.47 22,12C22,17.53 17.53,22 12,22C6.47,22 2,17.53 2,12C2,6.47 6.47,2 12,2M17,7H14.5L13.5,6H10.5L9.5,7H7V9H17V7M9,18H15A1,1 0 0,0 16,17V10H8V17A1,1 0 0,0 9,18Z'%3E%3C/path%3E%3C/svg%3E");
		background-size: 1.4em 1.4em;
		border: none;
		opacity: 0;
		transition: opacity 0.2s;
		text-indent: -9999px;
		cursor: pointer;
	}

	label:hover button {
		opacity: 1;
	}
	.toplevel {
		display: flex;
		align-items: stretch;
	}
	.toplevel h2 {
		margin-top: 10px;
	}
	.selectionpane {
		/* border: 1px solid red; */
		height: 50%;
	}
	.researchpane {
		/* border: 1px solid purple; */
		height: 50%;
	}
	.researchtable {
		overflow-y: scroll;
	}
	td {
		/* border: 1px solid yellow; */
	}
	.headerrow td {
		border-bottom: 1px solid gray;
		font-size: larger;
	}
</style>
