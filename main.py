from typing import List
import util
import codeparser as cp

# on recupere les arguments passe dans la commande
args = util.get_args()
path = args.path

# on lis le fichier
issues: List[cp.Problem] = cp.parse_file(path)

# on retourne les problemes a la console
for issue in issues:
    print("ligne", issue.line, ":", issue.description, "dans :", issue.code)
