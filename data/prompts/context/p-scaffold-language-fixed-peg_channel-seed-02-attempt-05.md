## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → approach → descend → contact → push → retract | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 19 | -0.4994 | 0.25 | ❌ rejected |
| 4 | align → approach → descend → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.0959 | 0.39 | ✅ accepted |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.0353 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2873 | 0.24 | ✅ accepted |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | -0.2297 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.499) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.005
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.y
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_check
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Design Metrics

- **Composite score**: -0.499
- **task_score** (E): 0.255
- **fitness_score**: 0.438  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.062
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.333
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_approach_1 | 1.00 | 1.00 | 0.1364 |
| approach_1 | 1.00 | 1.00 | 0.1949 |
| descend_1 | 1.00 | 1.00 | 0.0244 |
| contact_1 | 0.67 | 1.00 | 0.0311 |
| push_1 | 0.00 | 1.00 | 0.1364 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.489, 0.072, 0.259) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| approach_1 | approach | 1.00 / step_budget | (0.489, 0.072, 0.259)→(0.501, 0.113, 0.070) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.548 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.501, 0.113, 0.070)→(0.496, 0.108, 0.047) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 0.550 |
| contact_1 | contact | 0.67 / step_budget | (0.496, 0.108, 0.047)→(0.494, 0.082, 0.032) | (0.498, 0.068, 0.034)→(0.502, 0.053, 0.036) | 0.148→0.133 | 1.00 / 2.000 | 1307.638 | 5.681 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.082, 0.032)→(0.497, -0.054, 0.030) | (0.502, 0.053, 0.036)→(0.507, -0.082, 0.036) | 0.133→0.008 | 1.00 / 3.333 | 41.177 | 41.177 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.072
- terminal_score: 0.300
- phase_score: 0.527
- phase_breakdown.approach_score: 0.428
- phase_breakdown.push_score: 0.570
- phase_breakdown.contact_score: 0.497

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.492
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.319
- **Median Q (composite search score)**: -0.508
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.296


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37255,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.02017,"approach_1.arc_height":0.07919,"approach_1.generator.speed":0.20638,"approach_1.lateral_offset_x":-0.00108,"approach_1.lateral_offset_y":-0.01104,"contact_1.contact_force_threshold":11.11929,"contact_1.contact_offset_y":0.00844,"contact_1.generator.speed":0.0382,"descend_1.descend_z":0.00228,"descend_1.generator.speed":0.02643,"pre_approach_1.arc_height":0.05203,"pre_approach_1.generator.speed":0.15876,"pre_approach_1.lateral_offset_x":0.00681,"pre_approach_1.lateral_offset_y":-0.00503,"push_1.generator.speed":0.04444,"push_1.push_depth":0.12597,"retract_1.arc_height":0.05647,"retract_1.generator.speed":0.19358,"retract_1.retract_height":0.14307},"optimized_scores":{"best_composite_score":-0.50794,"best_fitness_score":0.49206,"best_task_score":0.31906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":272.0,"contact_point_centroid":[0.49944,6e-05,0.04154],"force_p95":27.4416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.71214,"mean_force":5.56876,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49219,0.01075,0.02866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50698,-0.10053,0.05977],"force_p95":33.32144,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.59385,"mean_force":11.03311,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49604,-0.05315,0.03017]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":231.0,"contact_point_centroid":[0.52522,-0.02933,0.03145],"force_p95":25.91784,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.81192,"mean_force":4.18682,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49286,-0.00291,0.0288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":126.0,"contact_point_centroid":[0.50657,-0.02991,0.00987],"force_p95":19.62006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.95419,"mean_force":6.69845,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49222,0.01278,0.02881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.49727,0.04736,0.00974],"force_p95":4.42698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.1241,"mean_force":2.2896,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4892,0.0893,0.03536]},{"body_a":"attachment","body_b":"peg","contact_count":296.0,"contact_point_centroid":[0.49448,0.07223,0.04534],"force_p95":4.23002,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.82338,"mean_force":2.7952,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48967,0.08391,0.03326]},{"body_a":"peg","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.52023,0.02706,0.06343],"force_p95":0.94766,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.69802,"mean_force":0.33188,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49021,0.04424,0.02788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49565,0.06408,0.00935],"force_p95":0.64274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57307,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.49217,0.1235,0.30282]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.19535,0.30196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49503,0.06362,0.0094],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54567,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48773,0.12702,0.17167]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49622,0.06405,0.0094],"force_p95":0.54984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55086,"mean_force":0.54541,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48983,0.10763,0.05429]}],"total_contact_groups":11},"final_pose_error":0.02637,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,-0.08233,0.03568],"final_tcp_position":[0.49613,-0.05437,0.03021],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":41.71214,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":630.0,"object_pos_end":[0.49492,0.06382,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54315,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":335.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.48694,0.06575,0.25857],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":442.0,"n_steps_budget":630.0,"object_pos_end":[0.49533,0.06378,0.03398],"object_pos_start":[0.49492,0.06382,0.03392],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14404,"object_z_max":0.03398,"peak_contact_force":0.54859,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":442.0,"raw_peak_contact_force":0.5516,"subtask_id":"approach","tcp_end":[0.49025,0.11006,0.06337],"tcp_start":[0.48694,0.06575,0.25857],"tcp_to_object_dist_end":0.05506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":74.0,"n_steps_budget":690.0,"object_pos_end":[0.49524,0.06409,0.03399],"object_pos_start":[0.49533,0.06378,0.03398],"object_to_goal_dist_end":0.14429,"object_to_goal_dist_start":0.14398,"object_z_max":0.03399,"peak_contact_force":0.54281,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":74.0,"raw_peak_contact_force":0.55086,"tcp_end":[0.49026,0.10571,0.04447],"tcp_start":[0.49025,0.11006,0.06337],"tcp_to_object_dist_end":0.04321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":478.0,"n_steps_budget":600.0,"object_pos_end":[0.50163,0.04644,0.03586],"object_pos_start":[0.49524,0.06409,0.03399],"object_to_goal_dist_end":0.12652,"object_to_goal_dist_start":0.14429,"object_z_max":0.03591,"peak_contact_force":2.71417,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":742.0,"raw_peak_contact_force":5.1241,"subtask_id":"contact","tcp_end":[0.49101,0.07489,0.03038],"tcp_start":[0.49026,0.10571,0.04447],"tcp_to_object_dist_end":0.03086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.08233,0.03568],"object_pos_start":[0.50163,0.04644,0.03586],"object_to_goal_dist_end":0.00853,"object_to_goal_dist_start":0.12652,"object_z_max":0.03765,"peak_contact_force":41.71214,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":678.0,"raw_peak_contact_force":41.71214,"subtask_id":"push","tcp_end":[0.49613,-0.05437,0.03021],"tcp_start":[0.49101,0.07489,0.03038],"tcp_to_object_dist_end":0.03049,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29878,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.01973,"approach_1.arc_height":0.02659,"approach_1.generator.speed":0.16889,"approach_1.lateral_offset_x":0.01069,"approach_1.lateral_offset_y":-0.01066,"contact_1.contact_force_threshold":11.37189,"contact_1.contact_offset_y":0.0025,"contact_1.generator.speed":0.01243,"descend_1.descend_z":0.01527,"descend_1.generator.speed":0.03905,"pre_approach_1.arc_height":0.05496,"pre_approach_1.generator.speed":0.2963,"pre_approach_1.lateral_offset_x":-0.00667,"pre_approach_1.lateral_offset_y":-0.00212,"push_1.generator.speed":0.0762,"push_1.push_depth":0.11387,"retract_1.arc_height":0.06034,"retract_1.generator.speed":0.24108,"retract_1.retract_height":0.12623},"optimized_scores":{"best_composite_score":-0.61377,"best_fitness_score":0.38623,"best_task_score":0.14564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.5075,-0.10029,0.05967],"force_p95":39.70955,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.71031,"mean_force":30.57844,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49177,-0.05438,0.03072]},{"body_a":"attachment","body_b":"peg","contact_count":224.0,"contact_point_centroid":[0.49703,-0.00162,0.04169],"force_p95":20.467,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.62801,"mean_force":4.24122,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48973,0.00874,0.03099]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50323,-0.03542,0.00984],"force_p95":18.64669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.70864,"mean_force":5.6344,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4899,0.00589,0.03107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":165.0,"contact_point_centroid":[0.52515,-0.03259,0.02813],"force_p95":10.39707,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.4868,"mean_force":2.47527,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48997,-0.00784,0.03056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.49603,0.03176,0.00992],"force_p95":4.25474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.53972,"mean_force":1.93221,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49024,0.07704,0.04111]},{"body_a":"attachment","body_b":"peg","contact_count":902.0,"contact_point_centroid":[0.49291,0.06369,0.04489],"force_p95":4.02039,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.23439,"mean_force":1.7315,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49014,0.07553,0.03988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.49469,0.05894,0.00933],"force_p95":0.61526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59219,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.47733,0.12204,0.3049]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.49765,0.19444,0.30272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.49414,0.05898,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.5462,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47768,0.09129,0.16748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":46.0,"contact_point_centroid":[0.49255,0.05796,0.00939],"force_p95":0.54953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54994,"mean_force":0.54578,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49502,0.09401,0.06467]}],"total_contact_groups":10},"final_pose_error":0.02128,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50768,-0.08079,0.03674],"final_tcp_position":[0.49177,-0.05537,0.03067],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":41.71031,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":600.0,"object_pos_end":[0.49413,0.05906,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54838,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":353.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46077,0.06337,0.25887],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":810.0,"object_pos_end":[0.4941,0.0591,0.03389],"object_pos_start":[0.49413,0.05906,0.03385],"object_to_goal_dist_end":0.13936,"object_to_goal_dist_start":0.13932,"object_z_max":0.03389,"peak_contact_force":0.55004,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":0.55326,"subtask_id":"approach","tcp_end":[0.49724,0.0938,0.07084],"tcp_start":[0.46077,0.06337,0.25887],"tcp_to_object_dist_end":0.05078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05892,0.03389],"object_pos_start":[0.4941,0.0591,0.03389],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.13936,"object_z_max":0.03389,"peak_contact_force":0.54985,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":46.0,"raw_peak_contact_force":0.54994,"tcp_end":[0.49345,0.09528,0.05828],"tcp_start":[0.49724,0.0938,0.07084],"tcp_to_object_dist_end":0.04379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49616,0.03824,0.03545],"object_pos_start":[0.49427,0.05892,0.03389],"object_to_goal_dist_end":0.11839,"object_to_goal_dist_start":0.13917,"object_z_max":0.03581,"peak_contact_force":1.5517,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1898.0,"raw_peak_contact_force":7.53972,"subtask_id":"contact","tcp_end":[0.49025,0.0677,0.0342],"tcp_start":[0.49345,0.09528,0.05828],"tcp_to_object_dist_end":0.03008,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50768,-0.08079,0.03674],"object_pos_start":[0.49616,0.03824,0.03545],"object_to_goal_dist_end":0.00838,"object_to_goal_dist_start":0.11839,"object_z_max":0.03871,"peak_contact_force":41.71031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":518.0,"raw_peak_contact_force":41.71031,"subtask_id":"push","tcp_end":[0.49177,-0.05537,0.03067],"tcp_start":[0.49025,0.0677,0.0342],"tcp_to_object_dist_end":0.0306,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39583,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.02455,"approach_1.arc_height":0.04598,"approach_1.generator.speed":0.20801,"approach_1.lateral_offset_x":0.01329,"approach_1.lateral_offset_y":0.00483,"contact_1.contact_force_threshold":8.40899,"contact_1.contact_offset_y":0.00464,"contact_1.generator.speed":0.02419,"descend_1.descend_z":-0.00557,"descend_1.generator.speed":0.05529,"pre_approach_1.arc_height":0.05194,"pre_approach_1.generator.speed":0.25402,"pre_approach_1.lateral_offset_x":-0.01307,"pre_approach_1.lateral_offset_y":0.00358,"push_1.generator.speed":0.05807,"push_1.push_depth":0.14641,"retract_1.arc_height":0.05592,"retract_1.generator.speed":0.1674,"retract_1.retract_height":0.18481},"optimized_scores":{"best_composite_score":-0.3764,"best_fitness_score":0.4361,"best_task_score":0.30011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":299.0,"contact_point_centroid":[0.50475,0.01628,0.04303],"force_p95":15.8167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.10866,"mean_force":3.00262,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.02796,0.02863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50612,-0.10048,0.0593],"force_p95":32.82708,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.5112,"mean_force":15.22982,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50269,-0.05255,0.03008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.50543,-0.02421,0.00986],"force_p95":16.44635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.75275,"mean_force":4.82362,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50096,0.02084,0.02875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":207.0,"contact_point_centroid":[0.52513,0.01046,0.02554],"force_p95":8.04344,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.96473,"mean_force":1.52395,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50048,0.03965,0.02836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.50585,0.0715,0.00962],"force_p95":3.00611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.37797,"mean_force":1.3494,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50208,0.11217,0.03196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":274.0,"contact_point_centroid":[0.50543,0.08083,0.00933],"force_p95":0.60458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60245,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.51139,0.13409,0.30206]},{"body_a":"attachment","body_b":"peg","contact_count":196.0,"contact_point_centroid":[0.50465,0.09505,0.04097],"force_p95":3.30617,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.07012,"mean_force":1.93374,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50177,0.10698,0.03104]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"pre_approach_1","phase_type":"approach","tcp_position_centroid":[0.50013,0.1943,0.30285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.50594,0.0809,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54676,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51781,0.13265,0.17442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50611,0.08081,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54678,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51045,0.12991,0.05618]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.07428,0.01045],"force_p95":0.40818,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40818,"mean_force":0.40818,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5018,0.10338,0.03072]}],"total_contact_groups":11},"final_pose_error":0.02042,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50608,-0.08284,0.03472],"final_tcp_position":[0.50271,-0.05376,0.03009],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3918.64754,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54661,"phase_name":"pre_approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":310.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52012,0.08799,0.25934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":630.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":361.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach","tcp_end":[0.51624,0.1355,0.07495],"tcp_start":[0.52012,0.08799,0.25934],"tcp_to_object_dist_end":0.06915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":125.0,"raw_peak_contact_force":0.55007,"tcp_end":[0.50552,0.12434,0.03743],"tcp_start":[0.51624,0.1355,0.07495],"tcp_to_object_dist_end":0.04362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.07339,0.0354],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.15362,"object_to_goal_dist_start":0.16112,"object_z_max":0.0354,"peak_contact_force":3918.64754,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":619.0,"raw_peak_contact_force":4.37797,"subtask_id":"contact","tcp_end":[0.50181,0.10305,0.03069],"tcp_start":[0.50552,0.12434,0.03743],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.08284,0.03472],"object_pos_start":[0.50696,0.07339,0.0354],"object_to_goal_dist_end":0.00854,"object_to_goal_dist_start":0.15362,"object_z_max":0.03668,"peak_contact_force":40.10866,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":663.0,"raw_peak_contact_force":40.10866,"subtask_id":"push","tcp_end":[0.50271,-0.05376,0.03009],"tcp_start":[0.50181,0.10305,0.03069],"tcp_to_object_dist_end":0.02964,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```