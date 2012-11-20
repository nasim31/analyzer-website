
import webapp2, os

from webapp2_extras import routes

from library.controller.index import IndexController
from library.controller.analizeDomain import AnalyzeDomainController
from library.controller.viewDomain import ViewDomainController

debugActive = os.environ['SERVER_SOFTWARE'].startswith( 'Dev' ) 

routes = [
	( '/', IndexController ),
	( '/analyze', AnalyzeDomainController ),
	( '/initProcessing', 'library.controller.initProcessing.InitProcessingController' ),
	routes.DomainRoute( 'live-report.domaingrasp.<:dev|com>',
		[
			webapp2.Route( '/<domainUrl>', handler = ViewDomainController, name = 'liveReport' ),
		]
	),
	routes.DomainRoute( 'report.domaingrasp.<:dev|com>',
		[
			webapp2.Route( '/<domainUrl>', handler = ViewDomainController, name = 'staticReport' ),
		]
	),
]
app = webapp2.WSGIApplication( routes, debug = debugActive )

