from pewpewbot.utils import split_text


def test_split():
    args = [
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 
        "aaa",
        """a
        a
        a
        a""", 
        """a
        a
        a
        a
        a a a a 
        a
        a"""]
    for arg in args:
        ans = split_text(arg, 4)
        assert "".join(ans) == arg  # Assert correct split chunks
        assert all(len(a) <= 4 for a in ans)  # Assert correct length of chunks
