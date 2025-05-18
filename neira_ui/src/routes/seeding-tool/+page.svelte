<script>
	import { quintOut } from 'svelte/easing';
	import { crossfade } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import Modal from './modal.svelte';
	import { pathsOfLength } from './pathlength';

	export let data;

	let races = data.races;
	let foundersDay = data.foundersDay;

	let tuples = [...foundersDay];

	let showModal = false;

	let textareaContents = '';

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
							race.day,
							race.url
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

	// let schools = [
	// 	'Nobles',
	// 	'Groton',
	// 	'Brooks',
	// 	'BB&N',
	// 	'Middlesex',
	// 	'Taft',
	// 	'Cambridge RLS',
	// 	'Choate',
	// 	'Hopkins',
	// 	'Winsor',
	// 	'Frederick Gunn',
	// 	"Miss Porter's",
	// 	'Brewster Academy',
	// 	'Canterbury',
	// 	'Greenwich Academy',
	// 	'Lyme/Old Lyme',
	// 	"St. Mark's",
	// 	'NMH',
	// 	'Berkshire Academy',
	// 	'Newton Country Day',
	// 	'Pomfret'
	// ];
	let schools = [
		"Brooks",
		"Nobles",
		"Groton",
		"Winsor",
		"NMH",
		"BB&N",
		"St. Mark's",
		"Hotchkiss",
		"Miss Porter's",
		"Taft",
		"Choate",
		"Berkshire Academy",
		"Frederick Gunn",
		"Greenwich Academy",
		"Hopkins",
		"Brewster Academy",
		"Middlesex",
		"Cambridge RLS",
		"Lyme/Old Lyme"
	]

	let unseeded = schools.map((school) => ({
		id: uid++,
		description: school
	}))

	let seeding = [];

	let selected = [unseeded[0]];

	loadState();

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
		localStorage.setItem("seeding", JSON.stringify(seeding));
		localStorage.setItem("unseeded", JSON.stringify(unseeded));
		localStorage.setItem("selected", JSON.stringify(selected));
	}

	function moveToUnseeded(x) {
		console.log('moveToUnseeded(' + JSON.stringify(x) + ')');
		let newValue = { ...selected[0], seeded: false };
		let index = seeding.map((x) => x.id).indexOf(newValue.id);
		unseeded = [...unseeded.slice(0, index), newValue, ...unseeded.slice(index)];
		seeding = seeding.filter((x) => x.id != newValue.id);
		selected = [newValue];
		saveState();
	}

	// function mark(todo, done) {
	// 	todo.done = done;
	// 	remove(todo);
	// 	todos = todos.concat(todo);
	// }

	function onKeyDown(e) {
		if (showModal) return;
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
					localStorage.setItem("seeding", JSON.stringify(seeding));
					break;
				case 40: // down = 40
					seeding = moveDown(seeding, index);
					localStorage.setItem("seeding", JSON.stringify(seeding));
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
					localStorage.setItem("unseeded", JSON.stringify(unseeded));

					break;
				case 40: // down = 40
					unseeded = moveDown(unseeded, index);
					localStorage.setItem("unseeded", JSON.stringify(unseeded));
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

	function saveState() {
		localStorage.setItem("seeding", JSON.stringify(seeding));
		localStorage.setItem("unseeded", JSON.stringify(unseeded));
		localStorage.setItem("selected", JSON.stringify(selected));
	}

	function loadState() {
		let storedUnseeded = JSON.parse(localStorage.getItem("unseeded"));
		let storedSeeding = JSON.parse(localStorage.getItem("seeding"));
		let storedSelected = JSON.parse(localStorage.getItem("selected"));

		if (storedSeeding !== null) {
			unseeded = storedUnseeded;
			seeding = storedSeeding;
			selected = storedSelected;
		}
	}
</script>

<!-- <h1>Yo</h1> -->
<div
	class="w3-row-padding w3-margin-bottom toplevel"
	style="height: calc(100vh - 43px); overflow: hidden"
>
	<div class="w3-col s4" style="justify-content: left">
		<!-- <select style="margin-top:10px">
			<option>G1</option>
			<option>G2</option>
			<option>G3</option>
			<option>G4</option>
		</select> -->
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
									saveState();
								} else {
									selected = [todo];
									saveState();
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
				<h2
					on:click={() => {
						textareaContents = seeding.map((x) => x.description).join('\n');
						showModal = true;
					}}
				>
					Seeding
				</h2>
				<!-- <p>
					<a href="" use:copy={seeding.map((x) => x.description).join('\n')}>Copy to clipboard</a>
				</p> -->

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
						{seeding.indexOf(todo) + 1}.
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
			{#if selected.length === 1}
				<h2>{selected[0].description}</h2>

				<p>
					{selected[0].description} has raced {tuples.filter((x) =>
						x.includes(selected[0].description)
					).length} times this season against {new Set(
						tuples.filter((x) => x.includes(selected[0].description)).flatMap((x) => [x[0], x[1]])
					).size - 1} unique opponents.
				</p>

				<ul>
					{#each tuples.filter((x) => x.includes(selected[0].description)) as tuple}
						<li>{tuple[0]},{tuple[1]},{tuple[2]},{tuple[3]} (<a href={tuple[4]}>link</a>)</li>
					{/each}
				</ul>
			{/if}
			{#if selected.length === 2}
				<h2>{selected[0].description} vs {selected[1].description}</h2>

				<p>
					{selected[0].description} has raced {selected[1].description}
					{tuples
						.filter((x) => x.includes(selected[0].description))
						.filter((x) => x.includes(selected[1].description)).length} time{tuples
						.filter((x) => x.includes(selected[0].description))
						.filter((x) => x.includes(selected[1].description)).length === 1
						? ''
						: 's'} this season.
				</p>

				<ul>
					{#each tuples
						.filter((x) => x.includes(selected[0].description))
						.filter((x) => x.includes(selected[1].description)) as tuple}
						<li>
							{tuple[0]} won by {tuple[2]} seconds on {tuple[3]} (<a href={tuple[4]}>link</a>)
						</li>
					{/each}
				</ul>

				<p>
					Here are the paths of length 2 from {selected[0].description} to {selected[1].description}
				</p>
				<ul>
					{#each pathsOfLength(2, tuples, selected[0].description, selected[1].description) as x}
						<li>
							{@html (function () {
								let result = selected[0].description;
								for (const y of x) {
									result += `-(<a href="${y[4]}">` + y[2] + '</a>)->' + y[1];
								}

								return result;
							})()}
						</li>
					{/each}
				</ul>
			{/if}
		</div>
		<!-- <div class="researchpane">
			<input
				placeholder="this box does nothing yet..."
				on:keydown={(e) => e.key === 'Enter' && add(e.target)}
			/>
			<div class="researchtable" style="height:calc(100vh - 43px)">
				<table style="border-collapse:collapse">
					<thead>
						<tr class="headerrow">
							<td>Faster School</td>
							<td>Slower School</td>
							<td>Margin</td>
							<td>Date</td>
							<td>Link</td>
						</tr>
					</thead>
					<tbody>
						{#each tuples as tuple}
							<tr>
								<td>{tuple[0]}</td>
								<td>{tuple[1]}</td>
								<td>{tuple[2]}</td>
								<td>{tuple[3]}</td>
								<td>(<a href={tuple[4]}>link</a>)</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div> -->
	</div>
</div>

<Modal
	bind:showModal
	apply={() => {
		let allSchools = unseeded.map((x) => x.description) + seeding.map((x) => x.description);
		let result = [];
		for (let school of textareaContents.split('\n')) {
			school = school.trim();
			if (school === '') continue;
			if (!allSchools.includes(school)) {
				return [false, `"${school}" was not recognized`];
			}
			result.push(school);
		}
		let newUnseeded = [];
		let newSeeding = [];
		let all = unseeded.concat(seeding);
		for (const school of all) {
			if (!result.includes(school.description)) {
				newUnseeded.push(school);
			} else {
				newSeeding.push(school);
			}
		}
		newSeeding.sort((a, b) => result.indexOf(a.description) - result.indexOf(b.description));
		console.log({ result, all, newUnseeded, newSeeding });
		seeding = newSeeding;
		unseeded = newUnseeded;
		return [true, 'whoopee'];
	}}
>
	<h2 slot="header">
		<!-- modal
		<small><em>adjective</em> mod·al \ˈmō-dəl\</small> -->
		Copy/paste seeding
	</h2>
	<textarea class="modaltextarea" bind:value={textareaContents}></textarea>
</Modal>

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
		padding-right: 10px;
		height: 100%;
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
		overflow-y: scroll;
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
	.modaltextarea {
		width: 100%;
		height: 150px;
		padding: 12px 20px;
		box-sizing: border-box;
		border: 2px solid #ccc;
		border-radius: 4px;
		background-color: #f8f8f8;
		font-size: 16px;
		resize: none;
	}
</style>
