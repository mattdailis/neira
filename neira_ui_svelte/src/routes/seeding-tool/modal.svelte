<script>
	export let showModal; // boolean

	export let apply;

	let error = '';

	let dialog; // HTMLDialogElement

	$: if (dialog && showModal) {
		error = '';
		dialog.showModal();
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
	bind:this={dialog}
	on:close={() => (showModal = false)}
	on:click|self={() => dialog.close()}
>
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div on:click|stopPropagation>
		<slot name="header" />
		<hr />
		<p hidden={error === '' ? true : false}><b>{error}</b></p>
		<slot />
		<hr />
		<!-- svelte-ignore a11y-autofocus -->
		<div style="display:flex; justify-content:space-between">
			<button autofocus on:click={() => dialog.close()}>close modal</button>
			<button
				autofocus
				on:click={() => {
					const [status, message] = apply();
					if (status) {
						dialog.close();
					} else {
						error = message;
					}
				}}>apply changes</button
			>
		</div>
	</div>
</dialog>

<style>
	dialog {
		max-width: 32em;
		border-radius: 0.2em;
		border: none;
		padding: 0;
	}
	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}
	dialog > div {
		padding: 1em;
	}
	dialog[open] {
		animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	@keyframes zoom {
		from {
			transform: scale(0.95);
		}
		to {
			transform: scale(1);
		}
	}
	dialog[open]::backdrop {
		animation: fade 0.2s ease-out;
	}
	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	button {
		display: block;
	}
</style>
