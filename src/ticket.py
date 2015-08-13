from ticket_server import TicketServer

import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('../config/default.cfg')
library_card_number1 = config.get('library', 'library1')
library_card_password1 = config.get('library', 'password1')

library_card_number2 = config.get('library', 'library2')
library_card_password2 = config.get('library', 'password2')

library_card_number3 = config.get('library', 'library3')
library_card_password3 = config.get('library', 'password3')

library_cards = {library_card_number1:library_card_password1,
                library_card_number2:library_card_password2,
                library_card_number3:library_card_password3,
    }

if __name__ == "__main__":
    #url = 'http://www.libraryinsight.net/mpSignUp.asp?t=1173435&jx=y9p&mps=1927&cFocus=title&pInstitution=Henry%20Art%20Gallery&etad=9/10/2015&pc=4827'
    dates_url = 'http://www.libraryinsight.net/mpCalendar.asp?t=2825676&jx=y9p&pInstitution=Henry%20Art%20Gallery&mps=1927'
    
    import ConfigParser
    
    config = ConfigParser.RawConfigParser()
    config.read('../config/default.cfg')

    server = TicketServer(config.get('Parse', 'PARSE_APP_ID'), 
                                        config.get('Parse', 'PARSE_REST_API_KEY'), 
                                        config.get('Parse', 'PARSE_MASTER_KEY')
                                        )
        
    #results = server.get_available_dates(dates_url)
    #for date, reserve_url in results.items():
    #    print date, reserve_url
    
    #server.update_museum_info_full()
    server.schedule_update_passid(dt=60*5)
    
    #results = server.buy_ticket(url, library_cards.items())
    
    #for card, ret in results.items():
    #    print card, ret
    
    