from typing import List
import util
import codeparser

args=util.get_args()
path=args.path

actions:List[codeparser.Problem]=codeparser.parse_file(path)