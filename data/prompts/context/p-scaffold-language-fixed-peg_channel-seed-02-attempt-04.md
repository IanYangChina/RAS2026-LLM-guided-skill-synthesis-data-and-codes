## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → descend → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.0959 | 0.39 | ✅ accepted |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.0353 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2873 | 0.24 | ✅ accepted |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | -0.2297 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2813 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.096) — your mutation base

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

- **Composite score**: 0.096
- **task_score** (E): 0.393
- **fitness_score**: 0.599  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2560 |
| approach_1 | 1.00 | 1.00 | 0.0085 |
| descend_1 | 1.00 | 1.00 | 0.0180 |
| contact_1 | 1.00 | 1.00 | 0.0019 |
| push_1 | 1.00 | 1.00 | 0.1826 |
| retract_1 | 1.00 | 1.00 | 0.2420 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.116, 0.060) | (0.494, 0.068, 0.040)→(0.499, 0.068, 0.034) | 0.151→0.148 | 1.00 / 2.000 | 325.920 | 378.205 |
| approach_1 | approach | 1.00 / step_budget | (0.495, 0.116, 0.060)→(0.501, 0.114, 0.055) | (0.499, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 72.594 | 337.012 |
| descend_1 | descend | 1.00 / step_budget | (0.501, 0.114, 0.055)→(0.494, 0.112, 0.040) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 39.537 | 76.293 |
| contact_1 | contact | 1.00 / force_exceeded | (0.494, 0.112, 0.040)→(0.493, 0.112, 0.038) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 42.105 | 42.105 |
| push_1 | push | 1.00 / step_budget | (0.493, 0.112, 0.038)→(0.500, -0.071, 0.040) | (0.498, 0.068, 0.034)→(0.501, -0.077, 0.028) | 0.148→0.014 | 1.00 / 3.667 | 133.791 | 287.545 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.071, 0.040)→(0.498, 0.001, 0.270) | (0.501, -0.077, 0.028)→(0.498, -0.076, 0.027) | 0.014→0.015 | 1.00 / 1.000 | 0.563 | 62.196 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.855
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.592
- phase_score: 0.852
- phase_breakdown.approach_score: 0.754
- phase_breakdown.push_score: 0.953
- phase_breakdown.contact_score: 0.647

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.592
- **Median Q (composite search score)**: 0.094
- **K-run variance**: 0.0146
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60099,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00184,"align_1.lateral_offset_y":-0.00815,"approach_1.approach_height":0.1284,"approach_1.generator.speed":0.1352,"contact_1.contact_force_threshold":3.76842,"contact_1.contact_offset_y":0.00685,"contact_1.generator.speed":0.03845,"descend_1.descend_z":-0.00143,"push_1.generator.speed":0.03004,"push_1.push_depth":0.17322,"retract_1.retract_height":0.14817},"optimized_scores":{"best_composite_score":0.24494,"best_fitness_score":0.74827,"best_task_score":0.59224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47497,0.11814,0.05994],"force_p95":387.93976,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":389.58051,"mean_force":279.62108,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48286,0.11081,0.05598]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.53634,0.03341,0.05998],"force_p95":187.44863,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.9819,"mean_force":152.15071,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49056,0.0336,0.03868]},{"body_a":"channel_base_body","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53815,-0.1,0.06498],"force_p95":258.43185,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.15994,"mean_force":185.03666,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4944,-0.07194,0.03973]},{"body_a":"attachment","body_b":"peg","contact_count":314.0,"contact_point_centroid":[0.50091,-0.02272,0.03633],"force_p95":179.2667,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.0749,"mean_force":111.83503,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49273,-0.01845,0.0389]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50618,-0.02171,0.00842],"force_p95":152.17659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.14444,"mean_force":67.07857,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49196,0.00233,0.03882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":277.0,"contact_point_centroid":[0.52594,-0.0425,0.02327],"force_p95":92.21011,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.63561,"mean_force":68.47615,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49307,-0.02908,0.03894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.51248,-0.10072,0.02053],"force_p95":89.00937,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.48723,"mean_force":47.66568,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49357,-0.06952,0.03969]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54133,-0.1,0.06499],"force_p95":55.91279,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.91279,"mean_force":55.91279,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49773,-0.07933,0.0403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.49456,-0.07334,0.00802],"force_p95":0.82923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.26352,"mean_force":1.63111,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49654,-0.02556,0.14937]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50817,-0.07989,0.03631],"force_p95":53.40771,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.2415,"mean_force":28.14971,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.07948,0.04118]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52551,-0.10075,0.01885],"force_p95":43.2797,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.88565,"mean_force":13.27396,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49773,-0.0797,0.04058]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53261,0.10641,0.05999],"force_p95":37.82398,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.82398,"mean_force":37.82398,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48691,0.10485,0.03839]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47485,-0.0486,0.02476],"force_p95":11.11987,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.65321,"mean_force":2.9883,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49574,-0.04565,0.09506]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47493,0.05443,0.05998],"force_p95":10.49883,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.6208,"mean_force":6.9226,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48865,0.08305,0.03855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49143,-0.10049,0.01356],"force_p95":6.82266,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.81851,"mean_force":3.01205,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49756,-0.07962,0.0409]}],"total_contact_groups":22},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49327,-0.07292,0.02419],"final_tcp_position":[0.49827,0.00062,0.27029],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":389.58051,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":37.0,"n_steps_budget":600.0,"object_pos_end":[0.4949,0.06369,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.54577,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":60.0,"raw_peak_contact_force":389.58051,"subtask_id":"approach","tcp_end":[0.48739,0.1096,0.05114],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.49486,0.06373,0.034],"object_pos_start":[0.4949,0.06369,0.034],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.1439,"object_z_max":0.034,"peak_contact_force":0.55239,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":46.0,"raw_peak_contact_force":0.55239,"tcp_end":[0.48787,0.10641,0.04041],"tcp_start":[0.48739,0.1096,0.05114],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":18.0,"n_steps_budget":600.0,"object_pos_end":[0.49495,0.0641,0.03401],"object_pos_start":[0.49486,0.06373,0.034],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14395,"object_z_max":0.034,"peak_contact_force":37.82398,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":19.0,"raw_peak_contact_force":37.82398,"subtask_id":"contact","tcp_end":[0.48688,0.10476,0.03831],"tcp_start":[0.48787,0.10641,0.04041],"tcp_to_object_dist_end":0.04168,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.50825,-0.07634,0.01853],"object_pos_start":[0.49495,0.0641,0.03401],"object_to_goal_dist_end":0.0233,"object_to_goal_dist_start":0.14431,"object_z_max":0.04263,"peak_contact_force":199.00503,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1251.0,"raw_peak_contact_force":292.9819,"tcp_end":[0.49773,-0.07933,0.0403],"tcp_start":[0.48688,0.10476,0.03831],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.49327,-0.07292,0.02419],"object_pos_start":[0.50825,-0.07634,0.01853],"object_to_goal_dist_end":0.01859,"object_to_goal_dist_start":0.0233,"object_z_max":0.02549,"peak_contact_force":0.60729,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":519.0,"raw_peak_contact_force":55.91279,"tcp_end":[0.49827,0.00062,0.27029],"tcp_start":[0.49773,-0.07933,0.0403],"tcp_to_object_dist_end":0.25691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60488,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00046,"align_1.lateral_offset_y":-0.01213,"approach_1.approach_height":0.12421,"approach_1.generator.speed":0.23527,"contact_1.contact_force_threshold":4.31965,"contact_1.contact_offset_y":0.00255,"contact_1.generator.speed":0.04508,"descend_1.descend_z":-0.0104,"push_1.generator.speed":0.02979,"push_1.push_depth":0.17518,"retract_1.retract_height":0.11026},"optimized_scores":{"best_composite_score":0.09377,"best_fitness_score":0.59711,"best_task_score":0.27872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":79.0,"contact_point_centroid":[0.47497,0.11402,0.05994],"force_p95":384.5174,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.29666,"mean_force":315.51188,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4815,0.1057,0.05661]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":50.0,"contact_point_centroid":[0.52513,-0.0812,0.05994],"force_p95":271.37948,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.38616,"mean_force":201.00543,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50206,-0.081,0.04033]},{"body_a":"channel_base_body","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.54493,-0.10001,0.06497],"force_p95":256.17006,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.67853,"mean_force":183.59042,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50135,-0.07856,0.03997]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.53541,0.06423,0.05997],"force_p95":179.97865,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.03976,"mean_force":148.86699,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48933,0.06402,0.03919]},{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.49866,-0.0319,0.03966],"force_p95":98.69655,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.27568,"mean_force":51.22373,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49646,-0.02269,0.03968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.49422,-0.02391,0.0086],"force_p95":97.591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.216,"mean_force":35.95955,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4948,-0.00246,0.03958]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52507,-0.08144,0.05997],"force_p95":56.07035,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.08794,"mean_force":14.01759,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50197,-0.0812,0.04066]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50009,-0.09273,0.04223],"force_p95":47.21502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.99465,"mean_force":23.78235,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50181,-0.08095,0.04099]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":55.0,"contact_point_centroid":[0.47465,-0.07019,0.02605],"force_p95":21.62417,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.7751,"mean_force":9.61752,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50046,-0.07223,0.05211]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":218.0,"contact_point_centroid":[0.47473,-0.05566,0.02754],"force_p95":36.64004,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.35221,"mean_force":17.31017,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49746,-0.03484,0.03972]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53251,0.10157,0.05997],"force_p95":43.05011,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.05011,"mean_force":43.05011,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48644,0.10016,0.03914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.49329,-0.07366,0.0082],"force_p95":12.06815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.95419,"mean_force":1.60438,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49893,-0.0264,0.14951]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54571,-0.1,0.06499],"force_p95":33.9504,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.07423,"mean_force":23.30657,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50199,-0.08124,0.0406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]}],"total_contact_groups":19},"final_pose_error":0.0298,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49359,-0.07331,0.02413],"final_tcp_position":[0.49868,0.00044,0.27023],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":404.29666,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":98.0,"n_steps_budget":600.0,"object_pos_end":[0.49406,0.05913,0.03393],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13939,"object_to_goal_dist_start":0.13935,"object_z_max":0.03393,"peak_contact_force":0.54449,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":177.0,"raw_peak_contact_force":404.29666,"subtask_id":"approach","tcp_end":[0.48671,0.10377,0.05143],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05884,0.03393],"object_pos_start":[0.49406,0.05913,0.03393],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13939,"object_z_max":0.03393,"peak_contact_force":0.55078,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":45.0,"raw_peak_contact_force":0.55078,"tcp_end":[0.48729,0.10125,0.0408],"tcp_start":[0.48671,0.10377,0.05143],"tcp_to_object_dist_end":0.04348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.49406,0.05914,0.03393],"object_pos_start":[0.49397,0.05884,0.03393],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13911,"object_z_max":0.03393,"peak_contact_force":43.05011,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":43.05011,"subtask_id":"contact","tcp_end":[0.48641,0.10007,0.03905],"tcp_start":[0.48729,0.10125,0.0408],"tcp_to_object_dist_end":0.04195,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.49227,-0.07362,0.02659],"object_pos_start":[0.49406,0.05914,0.03393],"object_to_goal_dist_end":0.01674,"object_to_goal_dist_start":0.1394,"object_z_max":0.04081,"peak_contact_force":201.79508,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1117.0,"raw_peak_contact_force":286.38616,"tcp_end":[0.50197,-0.08127,0.04059],"tcp_start":[0.48641,0.10007,0.03905],"tcp_to_object_dist_end":0.01867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,-0.07331,0.02413],"object_pos_start":[0.49227,-0.07362,0.02659],"object_to_goal_dist_end":0.01838,"object_to_goal_dist_start":0.01674,"object_z_max":0.0267,"peak_contact_force":0.53262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":536.0,"raw_peak_contact_force":70.08794,"tcp_end":[0.49868,0.00044,0.27023],"tcp_start":[0.50197,-0.08127,0.04059],"tcp_to_object_dist_end":0.25697,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00384,"align_1.lateral_offset_y":0.0053,"approach_1.approach_height":0.15807,"approach_1.generator.speed":0.29453,"contact_1.contact_force_threshold":2.66542,"contact_1.contact_offset_y":0.01021,"contact_1.generator.speed":0.02111,"descend_1.descend_z":-0.00976,"push_1.generator.speed":0.01284,"push_1.push_depth":0.16213,"retract_1.retract_height":0.19971},"optimized_scores":{"best_composite_score":-0.051,"best_fitness_score":0.45233,"best_task_score":0.30864},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.53608,0.11993,0.0598],"force_p95":364.62154,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.61103,"mean_force":316.10752,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5286,0.12877,0.06252]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.5459,0.04265,0.05998],"force_p95":250.53074,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.26653,"mean_force":145.58661,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50033,0.04442,0.03822]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":514.0,"contact_point_centroid":[0.52502,0.05694,0.05999],"force_p95":210.51479,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.85466,"mean_force":138.93281,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.05777,0.03813]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":344.0,"contact_point_centroid":[0.53039,0.11998,0.05998],"force_p95":226.34061,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.77597,"mean_force":171.42883,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52351,0.13078,0.05654]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":309.0,"contact_point_centroid":[0.53511,0.11997,0.05994],"force_p95":216.66917,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.16008,"mean_force":204.15255,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52847,0.12956,0.06257]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54549,-0.04796,0.05999],"force_p95":60.58641,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.58641,"mean_force":60.58641,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50009,-0.052,0.03818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":555.0,"contact_point_centroid":[0.50101,0.01684,0.00958],"force_p95":11.91287,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.32744,"mean_force":2.26512,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.05729,0.03811]},{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.50131,0.02712,0.04013],"force_p95":21.68798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.74613,"mean_force":4.77294,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50032,0.03874,0.03826]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.11999,0.06],"force_p95":45.30796,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.44062,"mean_force":44.11397,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50724,0.12978,0.03772]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":78.0,"contact_point_centroid":[0.52529,0.02023,0.03564],"force_p95":8.50419,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.37855,"mean_force":2.24641,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50037,0.05113,0.03805]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":135.0,"contact_point_centroid":[0.47473,-0.00543,0.03345],"force_p95":10.26765,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.77279,"mean_force":1.74997,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50028,0.02518,0.03847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50578,0.08087,0.00937],"force_p95":0.55112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56482,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5151,0.15903,0.16341]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49991,0.19854,0.29567]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52513,-0.08108,0.05493],"force_p95":1.71543,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48333,"mean_force":0.25058,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49755,-0.02175,0.09742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.50597,-0.10025,0.04575],"force_p95":0.91137,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06669,"mean_force":0.21065,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49782,-0.02429,0.09597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.50535,-0.08042,0.00943],"force_p95":0.65813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65586,"mean_force":0.55514,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4978,-0.00802,0.15623]}],"total_contact_groups":20},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50693,-0.08196,0.03377],"final_tcp_position":[0.49852,0.00308,0.27064],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":423.61103,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":314.43154,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":976.0,"raw_peak_contact_force":423.61103,"tcp_end":[0.5292,0.12912,0.06281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":216.69076,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":619.0,"raw_peak_contact_force":217.16008,"subtask_id":"approach","tcp_end":[0.52809,0.13005,0.06232],"tcp_start":[0.5292,0.12912,0.06281],"tcp_to_object_dist_end":0.06103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.08089,0.03378],"object_pos_start":[0.50595,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":117.50899,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":725.0,"raw_peak_contact_force":227.77597,"tcp_end":[0.5074,0.12983,0.03791],"tcp_start":[0.52809,0.13005,0.06232],"tcp_to_object_dist_end":0.04914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.08089,0.03378],"object_pos_start":[0.50598,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":45.44062,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":45.44062,"subtask_id":"contact","tcp_end":[0.50699,0.12968,0.03745],"tcp_start":[0.5074,0.12983,0.03791],"tcp_to_object_dist_end":0.04895,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.50173,-0.08043,0.03787],"object_pos_start":[0.50598,0.08089,0.03378],"object_to_goal_dist_end":0.00278,"object_to_goal_dist_start":0.16112,"object_z_max":0.03978,"peak_contact_force":0.5715,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1911.0,"raw_peak_contact_force":283.26653,"tcp_end":[0.50023,-0.05143,0.03824],"tcp_start":[0.50699,0.12968,0.03745],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.08196,0.03377],"object_pos_start":[0.50173,-0.08043,0.03787],"object_to_goal_dist_end":0.00952,"object_to_goal_dist_start":0.00278,"object_z_max":0.03937,"peak_contact_force":0.54837,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":638.0,"raw_peak_contact_force":60.58641,"tcp_end":[0.49852,0.00308,0.27064],"tcp_start":[0.50023,-0.05143,0.03824],"tcp_to_object_dist_end":0.25181,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```