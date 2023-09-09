FROM cadquery/cadquery-server

# the original image is almost perfect, we just want a
# couple extra things to make CQ nicer to work with
RUN pip install scipy==1.10.0
RUN pip install git+https://github.com/gumyr/cq_warehouse.git#egg=cq_warehouse

# this will be /data/src because original image is
# working in /data; we want leeway to export to
# outside the server dir but still inside a volume
WORKDIR src

ENTRYPOINT ["cq-server"]