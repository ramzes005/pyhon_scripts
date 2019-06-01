import os
import easygui
import requests

URI = "https://www.filmweb.pl"
LIVE_SEARCH = "https://www.filmweb.pl/serials/search?q="


class TvShow(object):
    """ Class represents a TV show. Extracting data from HTML and getting episodes names for season.
    """

    def __init__(self, data):
        self.title = self.extract(data, '"filmPreview__title">', '</h3>')
        self.year = int(self.extract(data,'"filmPreview__year">', '</span>'))
        self.seasons = int(self.extract(data,'"filmPreview__seasonsCount">', '</div>').split(' ')[0])
        self.rate = self.extract(data,'"rateBox__rate">', '</span>')
        self.description = self.extract(data,'"filmPreview__description"><p>', '</p>')
        self.link = URI + self.extract(data,'"filmPreview__link" href="', '">')


    @classmethod
    def extract(cls, string, begin, end):
        tmp = string.split(begin)
        if len(tmp) > 1:
            return tmp[1].split(end)[0]
        else:
            return "Description not found!"

    def __str__(self):
        return self.title + " (" + str(self.year) + ") Rate= " + self.rate + " Seasons: " + str(self.seasons)


    def get_episode_names(self, season):
        """ Method for extracting episode names from HTML.
        :param season: Season's number
        :return: List of episodes
        """

        postfix = "/episodes/"
        postfix += str(season) if season is not None else ''
        print("SEASON: " + postfix)
        resp = requests.get(self.link + postfix).text

        # Extract every episode starts with episode's name to element of array
        names = resp.split('<div class="episode__title">')[1:]
        # Delete all text before first episode and text after for each one
        names = [x.split('<')[0].replace("&times;", "x").replace("&oacute;", "ó") for x in names]

        # Create and return dict with an episode number as a key and name as a value
        episodes = {}
        for n in names:
            e = n.split(" - ")
            if len(e) > 1:
                episodes[e[0]] = e[1]

        return episodes



class UserInterface(object):
    """ Class with UI for collecting data and show messages.
    """

    @classmethod
    def get_data_from_user(cls, title, msg):
        result = easygui.enterbox(title, msg)
        print("'" + str(result) + "'")
        if result is not None and len(result) > 0:
            return result
        else:
            return None

    @classmethod
    def insert_title(cls):
        """ Showing dialog box for insert title to search. """
        return cls.get_data_from_user("Enter title you want to search.", "Insert title")

    @classmethod
    def insert_quality(cls):
        """ Showing dialog box for insert quality of episodes. E.g 720p """
        return cls.get_data_from_user("<OPTIONAL> Add quality suffix if you want. E.g. 720p", "Insert quality")

    @classmethod
    def get_path_to_files(cls):
        """ Showing dialog box for chose a directory with episodes and returns path for it. """
        return easygui.diropenbox()

    @classmethod
    def no_results_msg(cls):
        """ Showing message box with no result message. """
        easygui.msgbox('No results.', 'Episodes')

    @classmethod
    def confirmation(cls):
        """ Showing yes-no box for rename confirmation. """
        return easygui.ynbox("Are you sure you want to rename files?", "Are you sure?")

    @classmethod
    def chose_season(cls, tv_show):
        """ Showing choice box for with seasons of series.
        :param tv_show: TV show chosen by user
        """
        if tv_show.seasons > 1:
            return easygui.choicebox("Chose season.", "Season", [x + 1 for x in range(tv_show.seasons)])
        else:
            return None

    @classmethod
    def confirm_episodes(cls, episodes):
        """ Showing episode names for all season.
        :param episodes: List of episodes names
        """
        easygui.textbox("Is this your episodes? Please be sure or check at Filmweb.pl.", "Episodes",
                        ''.join(str(k + " - " + v + "\n") for k, v in episodes.items()))

    @classmethod
    def chose_show_among_series(cls, series):
        """ Showing choice box for search result.
        :param series: Search result of TvShows
        """
        choice = easygui.choicebox("Chose series from list below. Please be sure of your choice.", "Series", series)
        print("'" + str(choice) + "'")
        if choice is not None and choice != 'Add more choices':
            return series[choice]
        else:
            return None




def get_files_from_directory(path):
    # Getting list of all file names from chosen directory
    files = os.listdir(path)

    # Return only files where name is episode number
    return [file for file in files if file[0].isdigit()]


def search_for_series(title):
    # Getting search result as HTML text
    response = requests.get(LIVE_SEARCH + title).text

    # Split only for TV series
    titles = response.split('class="hits__item" data-statsType="serials">')[1:]
    titles = [t.split('</ul>')[0].replace("&times;", "x").replace("&oacute;", "ó") for t in titles]

    # Creating objects of TvShow and return if dictionary is not empty
    print("Search result: " + str(len(titles)))
    results = {}
    for t in titles:
        show = TvShow(t)
        results[str(show)] = show

    if len(results) > 0:
        return results
    else:
        return None



def rename_files(episodes, path_to_files, season=None, quality=None):
    """ Method for rename files in path which names are digits with episodes from Filmweb.pl.

    :param episodes: Dictionary of episodes
    :param path_to_files: Path to files to rename
    :param season: The Number of series season adjust to 2 places 's01'
    :param quality: Suffix for add to the end of file name
    """

    files = get_files_from_directory(path_to_files)
    print(files)
    print(episodes)

    for f in files:
        old_name, extension = f.split(".")
        if old_name in episodes:
            if season is not None:
                prefix = "s" + str(season).rjust(2, '0') + "e" + old_name.rjust(2, '0') + " - "
            else:
                prefix = "s01" + "e" + old_name.rjust(2, '0') + " - "

            if quality is not None:
                suffix = " " + quality
            else:
                suffix = ""

            new_name = prefix + episodes[old_name].replace(":", " -").replace("?", "") + suffix

            rename_from = path_to_files + "\\" + old_name + "." + extension
            rename_to = path_to_files + "\\" + new_name + "." + extension
            os.rename(rename_from, rename_to)


def start():
    """ Step by step to rename files. """
    ui = UserInterface()

    path = None
    season = None
    episodes = None
    series_list = None
    users_tv_show = None
    title = ui.insert_title()

    if title is not None:
        series_list = search_for_series(title)

    if series_list is not None:
        users_tv_show = ui.chose_show_among_series(series_list)
    else:
        ui.no_results_msg()


    if users_tv_show is not None:
        season = ui.chose_season(users_tv_show)
        episodes = users_tv_show.get_episode_names(season)
        ui.confirm_episodes(episodes)

        path = ui.get_path_to_files()

    if path is not None:
        quality = ui.insert_quality()

        if ui.confirmation():
            rename_files(episodes, path, season, quality)


def main():
    start()


if __name__ == '__main__':
    main()
