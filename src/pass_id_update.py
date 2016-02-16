from ticket_server import TicketServer
import sys

if __name__ == "__main__":
    import ConfigParser
    
    config = ConfigParser.RawConfigParser()
    config.read('../config/default.cfg')

    server = TicketServer(config.get('Parse', 'PARSE_APP_ID'), 
                                        config.get('Parse', 'PARSE_REST_API_KEY'), 
                                        config.get('Parse', 'PARSE_MASTER_KEY')
                                        )
    
            
    museum_id = sys.argv[1]
    
    dt = 3*60
    server.schedule_function(server.update_museum_passid_with_id, dt, museum_id)
    
    server.upload_museum_passID()
    
    
    
    