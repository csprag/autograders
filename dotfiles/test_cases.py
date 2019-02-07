import autograder

import os
import sh
import yaml

from fuzzywuzzy import process

class FuzzyRecursiveFileFinder(autograder.TestCase):
    def test(self, repo_path):
        with sh.pushd(repo_path):
            seen_files = set()
            # account for nested dirs
            for root, dirs, files in os.walk('.'):
                if '.git' in dirs:
                    dirs.remove('.git') # ignore git

                if not files:
                    continue

                for f in files[:]: # slice so we don't screw up iteration by removing
                    if os.path.islink(os.path.join(root, f)):
                        # symlinks not supported
                        files.remove(f)
                        continue
                    if not os.path.getsize(os.path.join(root, f)) > 0:
                        # prune empty files
                        files.remove(f)
                        continue

                if not files: # check again after we pruned
                    continue

                files = [os.path.join(root, f).strip('./') for f in files]

                seen_files.update(files)

                for vf, points, msg in self.valid_files:
                    closest_match, match_score = process.extractOne(vf, files)
                    if match_score > 90:
                        # good enough
                        return self.result(msg, points)

            if len(seen_files) == 0:
                additional_text = "No non-empty, non-symlink files"
            else:
                additional_text = 'Non-empty, non-symlink files:\n'
                additional_text += '\n'.join([ '\t{}'.format(f) for f in seen_files])

            return self.result('No {} configuration file found'.format(self.ftype), 0,
                    additional_text=additional_text)

class ShellConfigFile(FuzzyRecursiveFileFinder):
    points_possible = 1.5
    ftype = 'shell'

    valid_files = [
        ('bashrc', 1.5, 'Matched shell config file "bashrc"'),
        ('zshrc', 1.5, 'Matched shell config file "zshrc"'),
        ('bash_profile', 1.5, 'Matched shell config file "bash_profile"'),
        ('profile', 1.5, 'Matched shell config file "profile"'),
    ]

class SshConfigFile(FuzzyRecursiveFileFinder):
    points_possible = 1.5
    ftype = 'ssh'

    valid_files = [
        ('ssh', 1.5, 'Matched ssh config file "ssh"'),
        ('ssh_config', 1.5, 'Matched ssh config file "ssh_config"'),
        ('ssh.cfg', 1.5, 'Matched ssh config file "ssh.cfg"'),
        ('ssh/config', 1.5, 'Matched ssh config file "ssh/config"'),
        ('config', 1.0, 'Matched file "config", assuming it\'s ssh. -0.5 for poor naming.'),
    ]

class AnyOtherConfigFile(FuzzyRecursiveFileFinder):
    points_possible = 1.0
    ftype = 'other'

    # NOTE: this is by no means a comprehensive list.
    #       you'll have to check this manually future terms
    #       and append any dotfiles not included in this list.
    valid_files = [
        ('alias', 1., 'Matched other config file "alias"'),
        ('bash_aliases', 1., 'Matched other config file "bash_aliases"'),
        ('bash_logout', 1., 'Matched other config file "bash_logout"'),
        ('emacs', 1., 'Matched other config file "emacs"'),
        ('emacs.d/init.el', 1., 'Matched other config file "emacs.d/init.el"'),
        ('functions', 1., 'Matched other config file "functions"'),
        ('gitconfig', 1., 'Matched other config file "gitconfig"'),
        ('pypirc', 1., 'Matched other config file "pypirc"'),
        ('twmrc', 1., 'Matched other config file "twmrc"'),
        ('vim', 1., 'Matched other config file "vim"'),
        ('vimrc', 1., 'Matched other config file "vimrc"'),
        ('vim/vimrc', 1., 'Matched other config file "vim/vimrc"'),
        ('vim/netrwhist', 1., 'Matched other config file "vim/netrwhist"'),
        ('vim_pathogen/netrwhist', 1., 'Matched other config file "vim_pathogen/netrwhist"'),
        ('install.sh', 1., 'Matched other config file "install.sh"'),
        ('bootstrap.sh', 1., 'Matched other config file "bootstrap.sh"'),
        ('setup_dotfiles.sh', 1., 'Matched other config file "setup_dotfiles.sh"'),
        ('commands_used.sh', 1., 'Matched other config file "commands_used.sh"'),
        ('gitignore', 1., 'Matched other config file "gitignore"'),
        ('mozilla', 1., 'Matched other config file "mozilla"'),
        ('wget-hsts', 1., 'Matched other config file "wget-hsts"'),
        ('atom/keymap.cson', 1., 'Matched other config file "atom/keymap.cson"'),
    ]
