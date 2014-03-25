
from library.task.base import BaseTask
from library.awis import AwisApi

from lxml import etree
from xml.dom.minidom import parseString

from library.countries import country_name_by_code

class AlexaAnalyzerTask( BaseTask ):

	def getName( self ): return 'traffic'

	def getDefaultData( self ):

		return {
			'worldRank': 'N/A',
			'loadTimeMs': 0,
			'loadTime': 'N/A',
			'visitorsLocation': 'N/A',
		}

	def updateView( self, beauty, data ):

		beauty.find( id = 'worldRank' ).string.replace_with( data['worldRank'] )
		beauty.find( id = 'loadTime' ).string.replace_with( data['loadTime'] )
		beauty.find( id = 'loadTime' ).string.replace_with( data['loadTime'] )
		beauty.find( id = 'visitorsLocation' ).string.replace_with( data['visitorsLocation'] )

		if 'relatedLinks' in data and data['relatedLinks'] is not None:
			beauty.find( id = 'relatedLinks' ).string.replace_with( data['relatedLinks'] )
		else:
			beauty.find( id = 'relatedLinks' ).string.replace_with( 'N/A' )

	def start( self, baseUrl ):

		queryUrl = 'http://' + baseUrl

		content = self.getDefaultData()
		actions = []

		api = AwisApi( 'AKIAJDGJO3ACZ7KIGHCA', 'dIc3teMI2OoSw0W7z9EXgP9cQnvUlja8uSQN2MBT' )
		respXml = api.url_info( queryUrl, 'RelatedLinks', 'Categories', 'Rank', 'RankByCountry', 'UsageStats', 'ContactInfo', 'Speed', 'Language', 'Keywords', 'OwnedDomains', 'LinksInCount', 'SiteData' )
		xml = etree.tostring( respXml )
		
		respStatus = respXml.find( '//{%s}StatusCode' % api.NS_PREFIXES['alexa'] ).text
		if 'Success' == respStatus:

			dom_doc = parseString( xml )
			rank_list_items = []
			for country in dom_doc.getElementsByTagName( 'aws:Country' ):
				country_code = country.getAttribute( 'Code' )
				country_name = country_name_by_code( country_code )
				ranks = country.getElementsByTagName( 'aws:Rank' )
				if len( ranks ) > 0 and ranks[0].firstChild is not None:
					rank = ranks[0].firstChild.nodeValue
					rank_list_items.append( '<li>%(rank)s<sup>th</sup> most visited website in <img src="/images/flags/%(countryCode)s.png" alt="%(countryName)s flag" /> %(countryName)s</li>' % { 'countryCode': country_code.lower(), 'countryName': country_name, 'rank': rank } )
			content['visitorsLocation'] = '<ul>' + ''.join( rank_list_items[:3] ) + '</ul>'

			related_list_items = []
			for related in dom_doc.getElementsByTagName( 'aws:RelatedLink' ):
				related_url = related.getElementsByTagName( 'aws:NavigableUrl' )[0].firstChild.nodeValue
				related_title = related.getElementsByTagName( 'aws:Title' )[0].firstChild.nodeValue
				related_list_items.append( '<li><a href="%s" rel="nofollow" class="external" target="_blank">%s</a></li>' % ( related_url, related_title ) )
			content['relatedLinks'] = '<ul>' + ''.join( related_list_items[:5] ) + '</ul>'

			content['worldRank'] = respXml.find( '//{%s}Rank' % api.NS_PREFIXES['awis'] ).text
			if content['worldRank'] is None:
				content['worldRank'] = 'Unknown'

			temp = respXml.find( '//{%s}MedianLoadTime' % api.NS_PREFIXES['awis'] ).text
			if temp is not None:
				content['loadTimeMs'] = long( temp )
				content['loadTime'] = temp + ' milliseconds'
				if int( respXml.find( '//{%s}Percentile' % api.NS_PREFIXES['awis'] ).text ) < 50:
					content['loadTime'] += ' (SLOW)'
					actions.append({ 'status': 'regular', 'description': 'You have to speed up your site (e.g. serving smaller images, reducing the number of HTTP requests, compressing CSS and JavaScript files, etc...)' })
				else:
					actions.append({ 'status': 'good' })
					content['loadTime'] += ' (FAST)'

		self.sendAndSaveReport( baseUrl, content, actions )

