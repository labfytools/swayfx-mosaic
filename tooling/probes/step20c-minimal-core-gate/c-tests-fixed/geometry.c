// WHY: directly execute the accepted private core's C numerical branches.
// CONTRACT: only primitive scene boxes and borrowed row/workspace fields are
// adapted; no geometry algorithm is reimplemented. This is not integration.
// INVARIANT: core-functions.inc bodies and core-guard.inc statement match the
// byte ranges and SHA256 recorded by extract.py in bindings.json.
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
struct wlr_box { int x,y,width,height; };
struct list { void **items; };
struct mosaic_row { struct { double scroll_x; } state; };
struct mosaic { struct list *rows; };
struct sway_workspace { struct { int layout; } current; struct mosaic *mosaic; };
struct side_gaps { int left,right,top,bottom; };
enum { L_SPLITH=1, L_MOSAIC=7 };
#include "core-functions.inc"
static unsigned checks;
#define CHECK(x) do { checks++; if (!(x)) { fprintf(stderr,"FAIL %s:%d %s\n",__FILE__,__LINE__,#x); exit(1); } } while(0)
static bool box_equal(struct wlr_box a, struct wlr_box b) {
    return a.x==b.x && a.y==b.y && a.width==b.width && a.height==b.height;
}
// WHY: guard is a statement in arrange_output, not a callable helper.
// CONTRACT: exact statement is included with its real row/clip field names.
// INVARIANT: only setup/return are adapters; conversion branches are unchanged.
static struct wlr_box applied_guard(struct mosaic_row *row) {
    struct wlr_box clip={0,0,800,600};
#include "core-guard.inc"
    return clip;
}
struct fixture { struct mosaic_row row; void *items[1]; struct list rows; struct mosaic mosaic; struct sway_workspace ws; };
static void setup(struct fixture *f, double scroll) {
    *f=(struct fixture){0}; f->row.state.scroll_x=scroll;
    f->items[0]=&f->row; f->rows.items=f->items;
    f->mosaic.rows=&f->rows; f->ws.mosaic=&f->mosaic;
    f->ws.current.layout=L_MOSAIC;
}
static void intersection_tests(void) {
    struct test { struct wlr_box a,b,want; bool success; } cases[]={
        {{0,0,20,20},{10,5,20,20},{10,5,10,15},true},
        {{-20,-30,20,40},{-10,-20,30,20},{-10,-20,10,20},true},
        {{0,0,10,10},{10,0,10,10},{0},false},
        {{0,0,10,10},{0,10,10,10},{0},false},
        {{INT_MIN,0,1,1},{INT_MAX-1,0,1,1},{0},false},
        {{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},true},
        {{INT_MAX-1,INT_MAX-1,1,1},{INT_MAX-1,INT_MAX-1,1,1},{INT_MAX-1,INT_MAX-1,1,1},true},
        {{INT_MAX,0,1,1},{0,0,1,1},{0},false},
        {{0,INT_MAX,1,1},{0,0,1,1},{0},false},
        {{0,0,0,10},{0,0,1,1},{0},false},
        {{0,0,-1,10},{0,0,1,1},{0},false},
        {{0,0,1,-1},{0,0,1,1},{0},false},
        {{0,0,1,1},{0,0,0,1},{0},false},
        {{0,0,1,1},{0,0,1,-1},{0},false},
    };
    for (size_t i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
        for(int alias=0;alias<3;alias++) {
            struct wlr_box a=cases[i].a,b=cases[i].b,d={91,92,93,94};
            struct wlr_box *dst=alias==1?&a:alias==2?&b:&d;
            struct wlr_box before=*dst;
            bool result=probe_clip_box_intersection(dst,&a,&b);
            CHECK(result==cases[i].success);
            CHECK(box_equal(*dst,result?cases[i].want:before));
        }
    }
    printf("intersection cases=14 aliases=3 PASS\n");
}
static void translation_tests(void) {
    struct test { struct wlr_box local,want; int x,y; bool success; } cases[]={
        {{2,3,10,20},{-8,8,10,20},-10,5,true},
        {{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},0,0,true},
        {{INT_MAX-1,0,1,1},{INT_MAX-1,0,1,1},0,0,true},
        {{INT_MAX,0,1,1},{0},0,0,false},
        {{0,INT_MAX,1,1},{0},0,0,false},
        {{INT_MIN,0,1,1},{0},-1,0,false},
        {{0,INT_MIN,1,1},{0},0,-1,false},
        {{INT_MAX,0,0,0},{INT_MAX,0,0,0},0,0,true},
        {{0,0,-1,1},{0},0,0,false},
        {{0,0,1,-1},{0},0,0,false},
        {{0,0,0,1},{0,0,0,1},0,0,true},
        {{1,0,0,0},{0},INT_MAX,0,false},
    };
    for (size_t i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
        for(int alias=0;alias<2;alias++) {
            struct wlr_box a=cases[i].local,d={91,92,93,94};
            struct wlr_box *dst=alias?&a:&d,before=*dst;
            bool result=scene_clip_translate(&a,cases[i].x,cases[i].y,dst);
            CHECK(result==cases[i].success);
            CHECK(box_equal(*dst,result?cases[i].want:before));
        }
    }
    printf("translation cases=12 aliases=2 PASS\n");
}
static void scroll_tests(void) {
    double values[]={0,1.75,-1.75,(double)INT_MAX,(double)INT_MIN,
        nextafter((double)INT_MAX,0),nextafter((double)INT_MAX,INFINITY),
        nextafter((double)INT_MIN,0),nextafter((double)INT_MIN,-INFINITY),
        NAN,INFINITY,-INFINITY,nextafter(0x1p63,0)};
    int expected[]={0,-1,1,-INT_MAX,INT_MAX,-INT_MAX+1,0,INT_MAX,0,0,0,0,0};
    struct wlr_box area={0}; struct side_gaps gaps={0};
    for(size_t i=0;i<sizeof(values)/sizeof(values[0]);i++) {
        struct fixture f; setup(&f,values[i]);
        struct wlr_box clip=applied_guard(&f.row);
        bool valid=isfinite(values[i]) && values[i]>=INT_MIN && values[i]<=INT_MAX;
        CHECK(clip.width==(valid?800:0)); CHECK(clip.height==(valid?600:0));
        if(valid) CHECK(clip.x==(int)values[i]);
        CHECK(workspace_tiling_scene_x(&f.ws,&area,&gaps)==expected[i]);
    }
    struct fixture bounds;
    setup(&bounds,(double)INT_MIN);
    area.x=INT_MAX; gaps.left=INT_MAX;
    CHECK(workspace_tiling_scene_x(&bounds.ws,&area,&gaps)==INT_MAX);
    setup(&bounds,(double)INT_MAX);
    area.x=INT_MIN; gaps.left=INT_MIN;
    CHECK(workspace_tiling_scene_x(&bounds.ws,&area,&gaps)==INT_MIN);
    setup(&bounds,1.75); area.x=-10; gaps.left=-3;
    CHECK(workspace_tiling_scene_x(&bounds.ws,&area,&gaps)==-14);
    setup(&bounds,-1.75);
    CHECK(workspace_tiling_scene_x(&bounds.ws,&area,&gaps)==-12);
    struct fixture f; setup(&f,NAN); f.ws.current.layout=L_SPLITH;
    area.x=INT_MAX; gaps.left=1;
    CHECK(workspace_tiling_scene_x(&f.ws,&area,&gaps)==INT_MAX);
    f.ws.current.layout=L_MOSAIC; f.ws.mosaic=NULL;
    area.x=INT_MIN; gaps.left=-1;
    CHECK(workspace_tiling_scene_x(&f.ws,&area,&gaps)==INT_MIN);
    printf("scroll guard cases=13 safe camera casts=10 standard/no-mosaic=2 PASS\n");
}
// WHY: undefined conversions must not contaminate successful geometry tests.
// CONTRACT: one command-line reproducer executes one real core cast per process.
// INVARIANT: sanitizer stderr/raw exit are preserved, with no diagnostic suppression.
static int reproduce(const char *name) {
    double value;
    if(!strcmp(name,"nan")) value=NAN;
    else if(!strcmp(name,"pos-inf")) value=INFINITY;
    else if(!strcmp(name,"neg-inf")) value=-INFINITY;
    else if(!strcmp(name,"int64-upper")) value=0x1p63;
    else if(!strcmp(name,"int64-lower")) value=-0x1p63;
    else if(!strcmp(name,"below-int64-lower")) value=nextafter(-0x1p63,-INFINITY);
    else return 2;
    struct fixture f; setup(&f,value);
    struct wlr_box area={0}; struct side_gaps gaps={0};
    fprintf(stderr,"REPRO workspace_tiling_scene_x scroll=%s (%a)\n",name,value);
    fflush(stderr);
    int result=workspace_tiling_scene_x(&f.ws,&area,&gaps);
    CHECK(result==0);
    area.x=INT_MAX; gaps.left=INT_MAX;
    CHECK(workspace_tiling_scene_x(&f.ws,&area,&gaps)==INT_MAX);
    area.x=INT_MIN; gaps.left=INT_MIN;
    CHECK(workspace_tiling_scene_x(&f.ws,&area,&gaps)==INT_MIN);
    printf("RESULT %d bounded extremes PASS\n",result); return 0;
}
int main(int argc,char **argv) {
    if(argc==3 && !strcmp(argv[1],"--reproduce")) return reproduce(argv[2]);
    if(argc!=1) return 2;
    intersection_tests(); translation_tests(); scroll_tests();
    printf("PASS checks=%u\n",checks); return 0;
}
