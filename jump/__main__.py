import argparse
import csv
import sys
from typing import List, IO

from jump.book import Book
from jump.error import *
from jump.feed_processor import ProcessorFactory


def main():
    parser = argparse.ArgumentParser(description="Feed processor that reads messages from stdin")
    parser.add_argument('-f', '--infile', help='Input csv file, uses stdin if not present', type=str, required=False)
    parser.add_argument('-o', '--outfile', help='Output file, prints to stdout if not present', type=str,
                        required=False)
    parser.add_argument('-n', '--nostate', help='Do not output book state', action='store_true', required=False)
    parser.add_argument('-t', '--notrade', help='Do not output trades', action='store_true', required=False)
    args = vars(parser.parse_args())

    outfile = open(args['outfile'], 'w') if args['outfile'] else sys.stdout
    infile = open(args['infile'], 'r') if args['infile'] else sys.stdin
    book = Book(file=outfile)

    with infile as f:
        reader = csv.reader(f)
        ctr = 0
        errors = []
        for message in reader:
            try:
                processor = ProcessorFactory.create_processor(message, book)
                processor.process(message)
            except (InvalidOrderError, DuplicateOrderError, OrderDoesNotExistError, TradeNotMatchedError,
                    InvalidMessageError) as e:
                errors.append(e)

            book.midquote(outfile)
            ctr += 1
            if not ctr % 10 and not args['nostate']:
                book.output_state(outfile)

        try:
            book.expected_trades()
        except BestPriceButNoTradeError as e:
            errors.append(e)

        if not args['nostate']:
            book.output_state(outfile)
        report_errors(errors, outfile)


def report_errors(errors: List[Exception], file: IO):
    a = 0
    b = 0
    c = 0
    d = 0
    e = 0
    f = 0

    for error in errors:
        error_type = type(error)
        if error_type == InvalidMessageError:
            a += 1
        elif error_type == DuplicateOrderError:
            b += 1
        elif error_type == TradeNotMatchedError:
            c += 1
        elif error_type == OrderDoesNotExistError:
            d += 1
        elif error_type == BestPriceButNoTradeError:
            e += 1
        elif error_type == InvalidOrderError:
            f += 1

    file.write("ERRORS:\n")
    if a:
        file.write("a,{}\n".format(a))
    if b:
        file.write("b,{}\n".format(b))
    if c:
        file.write("c,{}\n".format(c))
    if d:
        file.write("d,{}\n".format(d))
    if e:
        file.write("e,{}\n".format(e))
    if f:
        file.write("f,{}\n".format(f))


if __name__ == '__main__':
    main()
