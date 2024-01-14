import os
from dotenv import load_dotenv

load_dotenv()

UW_API_URL = os.getenv('UW_API_URL')
UW_API_KEY = os.getenv('UW_API_KEY')

def get_course_info():
    pass


# if __name__ == '__main__':
#     me.connect(c.MONGO_DB_RMC)

#     parser = argparse.ArgumentParser()
#     supported_modes = ['departments', 'opendata2_courses', 'terms_offered',
#             'opendata_sections', 'scholarships']

#     parser.add_argument('mode', help='one of %s' % ','.join(supported_modes))
#     args = parser.parse_args()

#     if args.mode == 'departments':
#         get_departments()
#     elif args.mode == 'opendata2_courses':
#         get_opendata2_courses()
#     elif args.mode == 'terms_offered':
#         get_terms_offered()
#     elif args.mode == 'opendata_exam_schedule':
#         get_opendata_exam_schedule()
#     elif args.mode == 'opendata_sections':
#         get_opendata_sections()
#     elif args.mode == 'scholarships':
#         get_scholarships()
#     else:
#         sys.exit('The mode %s is not supported' % args.mode)