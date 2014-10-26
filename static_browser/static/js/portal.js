/*global ZeroClipboard */

$(function () {
	$('.package').on('click', '.resource', function (e) {
		var $el = $(this),
		  parent_package = $(this).parents('.package'),
			package_name = parent_package.data('package'),
			package_title = parent_package.data('package-title'),
			package_version = parent_package.data('version'),
			filename = $(this).data('resource'),
			base_url = '//tools.wmflabs.org/static/res/' + package_name + '/' + package_version + '/',
			url = base_url + filename,
			snippet;

		if ($(this).hasClass('resource-file')) {
			if (url.slice(-4) === '.css') {
				snippet = '<link rel="stylesheet" href="' + url + '">';
			} else if (url.slice(-3) === '.js') {
				snippet = '<script src="' + url + '">';
			} else {
				return;
			}
		} else if ($(this).hasClass('resource-font-file')) {
			var parent_font = $(this).parents('.resource-font'),
				font_name = parent_font.data('font-name'),
				font_eot_file = parent_font.find('.resource-font-file[data-font-type="eot"]').data('resource'),
				font_svg_file = parent_font.find('.resource-font-file[data-font-type="svg"]').data('resource'),
				font_ttf_file = parent_font.find('.resource-font-file[data-font-type="ttf"]').data('resource'),
				font_woff_file = parent_font.find('.resource-font-file[data-font-type="woff"]').data('resource');
			snippet = '@font-face {\n  font-family: \'' + font_name + '\';\n';
			if (font_eot_file) {
				snippet += '  src: url(\'' + base_url + font_eot_file + '\'); /* IE 5-8 */\n';
				if (font_svg_file || font_ttf_file || font_woff_file) {
					snippet += '  src: local(\'☺\'),             /* sneakily trick IE */\n';
				}
			} else {
				snippet += '  src:\n';
			}
			if (font_woff_file) {
				snippet += '    url(\'' + base_url + font_woff_file + '\') format(\'woff\')';
				if (font_svg_file || font_ttf_file) {
					snippet += ',';
				} else {
					snippet += ';';
				}
				snippet += '    /* FF 3.6, Chrome 5, IE9 */\n';
			}
			if (font_ttf_file) {
				snippet += '    url(\'' + base_url + font_ttf_file + '\') format(\'truetype\')';
				if (font_svg_file) {
					snippet += ',';
				} else {
					snippet += ';';
				}
				snippet += ' /* Opera, Safari */\n';
			}
			if (font_svg_file) {
				snippet += '    url(\'' + base_url + font_svg_file + '#font\') format(\'svg\');  /* iOS */\n';
			}
			snippet += '}'
		} else {
			return;
		}

		$('#resource-modal')
			.find('.resource-modal-package')
				.text(package_title)
				.end()
			.find('.resource-modal-version')
				.text(package_version)
				.end()
			.find('.resource-modal-file')
				.text(filename)
				.end()
			.find('.resource-modal-snippet')
				.text(snippet)
				.end()
			.find('.resource-view, .resource-download')
				.attr('href', url)
				.end()
			.find('.resource-download')
				.attr('download', filename)
				.end()
			.find('.btn-clipboard')
				.data('clipboard-value', snippet)
				.data('placement', 'top')
				.attr('title', 'Copy to clipboard')
				.tooltip({
					container: 'body'
				})
				.end()
			.modal();

		e.preventDefault();
	});

	ZeroClipboard.config({
		swfPath: '/static/res/zeroclipboard/2.1.5/ZeroClipboard.swf',
		hoverClass: 'btn-clipboard-hover'
	});

	var client = new ZeroClipboard($('.btn-clipboard'));

	client.on('copy', function (e) {
		var value = $.data(e.target, 'clipboard-value');
		e.client.setText(value);
	});

	// Notify successful copy and reset tooltip title
	client.on('aftercopy', function (e) {
		$(e.target)
			.attr('title', 'Copied!')
			.tooltip('fixTitle')
			.tooltip('show')
			.attr('title', 'Copy to clipboard')
			.tooltip('fixTitle');
	});

	// Notify copy failure
	ZeroClipboard.on('error', function (e) {
		$(e.target)
			.attr('title', e.message)
			.tooltip('fixTitle')
			.tooltip('show');
	});
});
