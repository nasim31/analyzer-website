
from library.controller.page import StandardPageController
from library.utilities import uriFor
from library.model.report import SiteReport

import uuid, logging

from google.appengine.api.channel import create_channel

from library.sections import reportSections

class LiveReportController( StandardPageController ):

	def get( self, domainUrl ):
		report = SiteReport.all().filter( 'url =', domainUrl ).get()
		if report is not None:
			url = uriFor( 'staticReport', domainUrl = domainUrl )
			self.redirect( url )
			return

		self.addJavaScript( '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js' )
		self.addJavaScript( '/_ah/channel/jsapi' )
		self.addJavaScript( '/bootstrap/js/bootstrap.min.js' )
		self.addJavaScript( '/scripts/liveReport.js' )
		
		self.addStyleSheet( '/bootstrap/css/bootstrap.min.css' )
		self.addStyleSheet( '/styles/allmedia.css' )

		channelId = self.request.cookies.get( 'channelId' )
		if channelId is None:
			channelId = uuid.uuid4().hex
			self.response.set_cookie( 'channelId', channelId )
		clientId = create_channel( channelId )

		from datetime import date

		values = {
			'domain': domainUrl,
			'domainLength': len( domainUrl.replace( '.com', '' ) ),
			'clientId': clientId,
			'sbOptions': reportSections,
			'pageTitle': '%(domainUrl)s | Domain insights for %(domainUrl)s by EGOsize.com' % { 'domainUrl': domainUrl },
			'pageDescription': 'Check %(domainUrl)s metrics on SEO, social and other relevant aspects thanks to EGO size'
		}

		html = self.renderTemplate( 'liveReport.html', values )
		self.writeResponse( html )


