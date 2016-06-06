var selected = null

$('img[usemap]').maphilight();

$('.modal').on('hidden.bs.modal', function () {
    $(selected).click()
    selected = null
    $(this).modal('hide')
})

$('area').click(function(e) {
    if (this.id.indexOf('edge') > -1) {
	e.preventDefault()
	if (this.selected != true) {
	    if (selected !== null && selected !== this) {
		$(selected).click()
		selected = null
	    }
	    selected = this
	    this.selected = true
	} else {
	    this.selected = false
	    selected = null
	}
	var data = $(this).mouseout().data('maphilight') || {};
	data.alwaysOn = !data.alwaysOn;
	$(this).data('maphilight', data).trigger('alwaysOn.maphilight');
	console.log("sup")
	var modal = $('.modal')
	var header = $(modal.find('.modal-header')[0]).find('h4')[0]
	var body = modal.find('.modal-body')[0]
	console.log(this.title)
	var tooltip = this.title.split("\t\t\t")
	console.log(tooltip[1])
	console.log((tooltip[1].match(/\n/g) || []).length)
	$(header).html(tooltip[0])
	var lines = tooltip[1].split('\n')
	if (lines[0] == "") {
	    lines.shift()
	}
	$(body).html(lines.join('<br>'))
	var button = modal.find('.link')[0]//btn-primary')
	$(button).attr("href",this.href)
	$('.modal').modal()
	console.log($('.modal-backdrop'))
    }
});
