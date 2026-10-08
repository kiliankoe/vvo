// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://oepnv.dresden.lol',
	integrations: [
		starlight({
			title: 'ÖPNV Dresden',
			// Same greens as the accent color, so the logo matches the title in both themes.
			logo: { light: './src/assets/logo.svg', dark: './src/assets/logo-dark.svg' },
			description: 'Community documentation, live status and data for public transit in the Verkehrsverbund Oberelbe (Dresden).',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/kiliankoe/vvo' }],
			// Entry paths are relative to site/ (e.g. ../documentation/webapi.md).
			editLink: { baseUrl: 'https://github.com/kiliankoe/vvo/edit/main/site/' },
			customCss: ['./src/styles/custom.css'],
			components: {
				Banner: './src/components/Banner.astro',
				SiteTitle: './src/components/SiteTitle.astro',
			},
			sidebar: [
				{
					label: 'Live',
					items: [
						{ label: 'Network status', link: '/status/' },
						{ label: 'Departures', link: '/departures/' },
						{ label: 'Endpoint health', link: '/health/' },
					],
				},
				{
					label: 'API docs',
					items: [
						{ label: 'Choosing an API', link: '/docs/api-comparison/' },
						{ label: 'WebAPI', link: '/docs/webapi/' },
						{ label: 'Widget API', link: '/docs/widgets/' },
						{ label: 'TRIAS', link: '/docs/trias/' },
						{ label: 'GTFS', link: '/docs/gtfs/' },
						{ label: 'SIRI ET', link: '/docs/siri/' },
						{ label: 'Dresden OpenData', link: '/docs/opendata/' },
						{ label: 'TLMS vehicle positions', link: '/docs/tlms/' },
					],
				},
				{
					label: 'Interactive reference',
					items: [
						{ label: 'WebAPI', link: '/reference/webapi/' },
						{ label: 'Widget API', link: '/reference/widgets/' },
						{ label: 'TRIAS', link: '/reference/trias/' },
						{ label: 'Dresden OpenData', link: '/reference/opendata/' },
					],
				},
				{
					label: 'Data',
					items: [
						{ label: 'Stop lookup', link: '/stops/' },
						{ label: 'Abbreviations', link: '/abbreviations/' },
						{ label: 'Downloads', link: '/downloads/' },
					],
				},
				{ label: 'Libraries, apps & tools', link: '/ecosystem/' },
			],
		}),
	],
});
