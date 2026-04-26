# Crawl Output Notes

- Detailed crawl mode collects 9 section hashes per park: homepage, alerts, information, seasonal_update, overnight_facilities, reservations, trails, recreation_facilities, amenities.
- Collect mode output is JSONL when `-o` is provided in `src/script/collect.js`.
- Parallel task execution is abstracted in `src/util/processors.js` via `new Processors(items).run(fn)`.
- On DNR park pages, rendered section containers often lack IDs matching `sectionId`; section detection should use active nav hash (`a.navlinkactive[href*="#..."]`) rather than only `getElementById(sectionId)`.
