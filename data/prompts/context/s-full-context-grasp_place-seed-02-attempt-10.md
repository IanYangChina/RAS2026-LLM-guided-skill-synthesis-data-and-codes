## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2200 | 0.36 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.0009 | 0.48 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1488 | 0.40 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0234 | 0.33 | ❌ rejected |
| 6 | approach → descend → grasp → lift → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.1916 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.220) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_object
  target_entity: object
  weight: 0.2
phases:
- id: approach_above_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: lift_object
- id: approach_above_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.220
- **task_score** (E): 0.360
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0756 |
| descend_to_grasp | 1.00 | 1.00 | 0.1998 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 1.00 | 1.00 | 0.0987 |
| approach_above_goal | 1.00 | 1.00 | 0.2632 |
| descend_to_place | 1.00 | 1.00 | 0.0553 |
| release | 1.00 | 1.00 | 0.0196 |
| retract_after_place | 1.00 | 1.00 | 0.0781 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.010, 0.234) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.494, -0.010, 0.234)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.333 | 0.137 | 0.190 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.125) | (0.493, -0.015, 0.026)→(0.486, -0.015, 0.116) | 0.281→0.252 | 1.00 / 41.333 | 0.073 | 0.682 |
| approach_above_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.125)→(0.620, 0.158, 0.252) | (0.486, -0.015, 0.116)→(0.606, 0.134, 0.155) | 0.252→0.120 | 1.00 / 22.000 | 3249.712 | 0.809 |
| descend_to_place | descend | 1.00 / step_budget | (0.620, 0.158, 0.252)→(0.629, 0.170, 0.199) | (0.606, 0.134, 0.155)→(0.612, 0.143, 0.118) | 0.120→0.081 | 1.00 / 20.000 | 3249.685 | 0.209 |
| release | release | 1.00 / step_budget | (0.629, 0.170, 0.199)→(0.624, 0.168, 0.218) | (0.612, 0.143, 0.118)→(0.611, 0.146, 0.014) | 0.081→0.163 | 1.00 / 4.000 | 0.100 | 1.176 |
| retract_after_place | retract | 1.00 / step_budget | (0.624, 0.168, 0.218)→(0.633, 0.174, 0.296) | (0.611, 0.146, 0.014)→(0.611, 0.146, 0.016) | 0.163→0.160 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.519
- phase_score: 0.425
- phase_breakdown.approach_object_score: 0.131
- phase_breakdown.grasp_object_score: 0.798
- phase_breakdown.release_object_score: 0.073
- phase_breakdown.lift_object_score: 0.367
- phase_breakdown.approach_goal_score: 0.634
- phase_breakdown.place_object_score: 0.495
- grasp_place_fitness: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.519
- **Median Q (composite search score)**: -0.243
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09063,"average_solve_count":320.0,"average_success_count":320.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.08389,"approach_above_goal.approach_goal_speed":0.04587,"approach_above_goal.arc_height":0.27702,"approach_above_object.approach_height":0.13896,"approach_above_object.approach_speed":0.25576,"descend_to_grasp.descent_speed":0.038,"descend_to_grasp.grasp_z_tolerance":0.00763,"descend_to_place.place_speed":0.05985,"descend_to_place.place_z_offset":0.03442,"descend_to_place.place_z_tolerance":0.01491,"lift.lift_height":0.12551,"lift.lift_speed":0.04817,"release.release_time":0.21648,"retract_after_place.retract_speed":0.06817},"optimized_scores":{"best_composite_score":-0.24272,"best_fitness_score":0.63728,"best_task_score":0.31331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.62994,0.15384,-0.00839],"force_p95":1.42751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97069,"mean_force":0.46882,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61888,0.15238,0.24009]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.47084,-0.01926,-0.00117],"force_p95":0.51929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64237,"mean_force":0.12015,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46252,-0.01952,0.02879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":963.0,"contact_point_centroid":[0.62518,0.17259,0.2244],"force_p95":0.08534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30246,"mean_force":0.05529,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62202,0.15345,0.2232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20765.0,"contact_point_centroid":[0.45979,-0.03859,0.0765],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28435,"mean_force":0.04918,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45993,-0.01944,0.07474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20267.0,"contact_point_centroid":[0.45989,-0.00028,0.07736],"force_p95":0.07163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28325,"mean_force":0.04997,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45993,-0.01944,0.07528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1037.0,"contact_point_centroid":[0.62514,0.13458,0.22397],"force_p95":0.07996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2525,"mean_force":0.0509,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62209,0.15347,0.22335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2505.0,"contact_point_centroid":[0.6196,0.16533,0.25145],"force_p95":0.09324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22469,"mean_force":0.06625,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61647,0.14628,0.25003]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00205],"force_p95":0.13862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18955,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46515,-0.01958,0.02827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2839.0,"contact_point_centroid":[0.61948,0.12745,0.25063],"force_p95":0.08509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18776,"mean_force":0.0589,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61647,0.14628,0.25003]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48902,-0.00777,0.24567]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.63196,0.1536,-0.00203],"force_p95":0.12429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12593,"mean_force":0.11813,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62278,0.15493,0.28298]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47345,-0.01798,0.11063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18323.0,"contact_point_centroid":[0.51151,0.05505,0.22855],"force_p95":0.08223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10385,"mean_force":0.0541,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5106,0.03589,0.22711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20371.0,"contact_point_centroid":[0.51203,0.01775,0.22862],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10352,"mean_force":0.04929,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.51147,0.03679,0.22771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.46374,-0.0003,0.02982],"force_p95":0.06596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09548,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46403,-0.01955,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5406.0,"contact_point_centroid":[0.46361,-0.03881,0.02931],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08308,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01955,0.02718]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63196,0.1536,0.01602],"final_tcp_position":[0.6281,0.15773,0.3204],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.97069,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47788,-0.01633,0.18817],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47187,-0.01972,0.03494],"tcp_start":[0.47788,-0.01633,0.18817],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01958,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13634,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12268.0,"raw_peak_contact_force":0.18955,"subtask_id":"grasp_object","tcp_end":[0.46401,-0.01955,0.02715],"tcp_start":[0.47187,-0.01972,0.03494],"tcp_to_object_dist_end":0.0121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4689,-0.01937,0.11399],"object_pos_start":[0.47603,-0.01958,0.02581],"object_to_goal_dist_end":0.25313,"object_to_goal_dist_start":0.28822,"object_z_max":0.11389,"peak_contact_force":0.07758,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41192.0,"raw_peak_contact_force":0.64237,"subtask_id":"lift_object","tcp_end":[0.45997,-0.01943,0.12304],"tcp_start":[0.46401,-0.01955,0.02715],"tcp_to_object_dist_end":0.01271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61958,0.1396,0.25836],"object_pos_start":[0.4689,-0.01937,0.11399],"object_to_goal_dist_end":0.07207,"object_to_goal_dist_start":0.25313,"object_z_max":0.26592,"peak_contact_force":0.08499,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38694.0,"raw_peak_contact_force":0.10385,"subtask_id":"approach_goal","tcp_end":[0.61101,0.13948,0.2743],"tcp_start":[0.45997,-0.01943,0.12304],"tcp_to_object_dist_end":0.0181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.63186,0.15383,0.21046],"object_pos_start":[0.61958,0.1396,0.25836],"object_to_goal_dist_end":0.02114,"object_to_goal_dist_start":0.07207,"object_z_max":0.25836,"peak_contact_force":0.08488,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5344.0,"raw_peak_contact_force":0.22469,"subtask_id":"place_object","tcp_end":[0.62367,0.15374,0.22749],"tcp_start":[0.61101,0.13948,0.2743],"tcp_to_object_dist_end":0.0189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63154,0.1526,0.01042],"object_pos_start":[0.63186,0.15383,0.21046],"object_to_goal_dist_end":0.17971,"object_to_goal_dist_start":0.02114,"object_z_max":0.21046,"peak_contact_force":0.07793,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2168.0,"raw_peak_contact_force":1.97069,"subtask_id":"release_object","tcp_end":[0.61886,0.15238,0.24666],"tcp_start":[0.62367,0.15374,0.22749],"tcp_to_object_dist_end":0.23657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":870.0,"object_pos_end":[0.63196,0.1536,0.01602],"object_pos_start":[0.63154,0.1526,0.01042],"object_to_goal_dist_end":0.17409,"object_to_goal_dist_start":0.17971,"object_z_max":0.01666,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12593,"subtask_id":"release_object","tcp_end":[0.6281,0.15773,0.3204],"tcp_start":[0.61886,0.15238,0.24666],"tcp_to_object_dist_end":0.30443,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16352,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.09053,"approach_above_goal.approach_goal_speed":0.04636,"approach_above_goal.arc_height":0.30058,"approach_above_object.approach_height":0.24246,"approach_above_object.approach_speed":0.22503,"descend_to_grasp.descent_speed":0.05538,"descend_to_grasp.grasp_z_tolerance":0.01107,"descend_to_place.place_speed":0.0661,"descend_to_place.place_z_offset":0.02919,"descend_to_place.place_z_tolerance":0.00777,"lift.lift_height":0.13555,"lift.lift_speed":0.05455,"release.release_time":0.43268,"retract_after_place.retract_speed":0.13731},"optimized_scores":{"best_composite_score":-0.13819,"best_fitness_score":0.74181,"best_task_score":0.51939},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.62637,0.21376,-0.00553],"force_p95":1.01196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4344,"mean_force":0.32445,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61669,0.20114,0.1587]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.45466,-0.02444,-0.0012],"force_p95":0.47228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66241,"mean_force":0.10552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44603,-0.02529,0.0295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.62368,0.22077,0.13943],"force_p95":0.25209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45565,"mean_force":0.08972,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62061,0.20266,0.14329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.62254,0.18438,0.13928],"force_p95":0.23543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44665,"mean_force":0.1056,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62063,0.20267,0.14326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20937.0,"contact_point_centroid":[0.44339,-0.04435,0.08187],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28944,"mean_force":0.04863,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44356,-0.02519,0.08001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2057.0,"contact_point_centroid":[0.621,0.17844,0.17781],"force_p95":0.14651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2787,"mean_force":0.08951,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61759,0.19676,0.18016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.62186,0.21566,0.17551],"force_p95":0.14427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27472,"mean_force":0.09257,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61795,0.19721,0.17787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20694.0,"contact_point_centroid":[0.4434,-0.00601,0.08231],"force_p95":0.07149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27059,"mean_force":0.04877,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44357,-0.02519,0.08032]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02616,-0.00208],"force_p95":0.14788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2193,"mean_force":0.12941,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44862,-0.02539,0.02887]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.45856,-0.02632,-0.0016],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12436,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48756,-0.00704,0.29064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15457.0,"contact_point_centroid":[0.51579,0.08415,0.21151],"force_p95":0.08873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13759,"mean_force":0.06324,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.51331,0.06519,0.21025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16471.0,"contact_point_centroid":[0.51067,0.0403,0.20788],"force_p95":0.08858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13674,"mean_force":0.06002,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50849,0.05919,0.20729]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.62865,0.21374,-0.00197],"force_p95":0.12539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12821,"mean_force":0.12102,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62038,0.20347,0.20574]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46311,-0.02065,0.15573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.44688,-0.00614,0.02914],"force_p95":0.06662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11028,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44754,-0.02535,0.02785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5226.0,"contact_point_centroid":[0.44726,-0.04465,0.02935],"force_p95":0.06765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0858,"mean_force":0.04282,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44754,-0.02535,0.02785]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62865,0.21374,0.01602],"final_tcp_position":[0.62601,0.20638,0.24482],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.4344,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02596],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47345,-0.01575,0.27984],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02596],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45511,-0.0256,0.03507],"tcp_start":[0.47345,-0.01575,0.27984],"tcp_to_object_dist_end":0.00971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02542,0.02569],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14491,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12303.0,"raw_peak_contact_force":0.2193,"subtask_id":"grasp_object","tcp_end":[0.44752,-0.02534,0.02782],"tcp_start":[0.45511,-0.0256,0.03507],"tcp_to_object_dist_end":0.01113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4534,-0.0252,0.12296],"object_pos_start":[0.45844,-0.02542,0.02569],"object_to_goal_dist_end":0.29291,"object_to_goal_dist_start":0.30312,"object_z_max":0.12288,"peak_contact_force":0.06905,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41790.0,"raw_peak_contact_force":0.66241,"subtask_id":"lift_object","tcp_end":[0.44357,-0.02518,0.1322],"tcp_start":[0.44752,-0.02534,0.02782],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62442,0.1918,0.19178],"object_pos_start":[0.4534,-0.0252,0.12296],"object_to_goal_dist_end":0.07958,"object_to_goal_dist_start":0.29291,"object_z_max":0.22698,"peak_contact_force":0.09323,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31928.0,"raw_peak_contact_force":0.13759,"subtask_id":"approach_goal","tcp_end":[0.61496,0.1917,0.20996],"tcp_start":[0.44357,-0.02518,0.1322],"tcp_to_object_dist_end":0.0205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.63092,0.2032,0.12692],"object_pos_start":[0.62442,0.1918,0.19178],"object_to_goal_dist_end":0.01377,"object_to_goal_dist_start":0.07958,"object_z_max":0.19178,"peak_contact_force":0.15289,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4157.0,"raw_peak_contact_force":0.2787,"subtask_id":"place_object","tcp_end":[0.62303,0.20338,0.14825],"tcp_start":[0.61496,0.1917,0.20996],"tcp_to_object_dist_end":0.02274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62851,0.21253,0.01503],"object_pos_start":[0.63092,0.2032,0.12692],"object_to_goal_dist_end":0.0992,"object_to_goal_dist_start":0.01377,"object_z_max":0.12692,"peak_contact_force":0.09832,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1619.0,"raw_peak_contact_force":1.4344,"subtask_id":"release_object","tcp_end":[0.61664,0.20112,0.16696],"tcp_start":[0.62303,0.20338,0.14825],"tcp_to_object_dist_end":0.15283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.62865,0.21374,0.01602],"object_pos_start":[0.62851,0.21253,0.01503],"object_to_goal_dist_end":0.09827,"object_to_goal_dist_start":0.0992,"object_z_max":0.01651,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.12821,"subtask_id":"release_object","tcp_end":[0.62601,0.20638,0.24482],"tcp_start":[0.61664,0.20112,0.16696],"tcp_to_object_dist_end":0.22894,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67172,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.08468,"approach_above_goal.approach_goal_speed":0.10426,"approach_above_goal.arc_height":0.21657,"approach_above_object.approach_height":0.18966,"approach_above_object.approach_speed":0.15258,"descend_to_grasp.descent_speed":0.0937,"descend_to_grasp.grasp_z_tolerance":0.0128,"descend_to_place.place_speed":0.07374,"descend_to_place.place_z_offset":0.02522,"descend_to_place.place_z_tolerance":0.0111,"lift.lift_height":0.11725,"lift.lift_speed":0.05965,"release.release_time":0.27286,"retract_after_place.retract_speed":0.09062},"optimized_scores":{"best_composite_score":-0.27905,"best_fitness_score":0.60095,"best_task_score":0.24821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1030.0,"contact_point_centroid":[0.57388,0.07185,-0.00315],"force_p95":0.66909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1859,"mean_force":0.18629,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60424,0.10419,0.27546]},{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.53874,0.0007,-0.00113],"force_p95":0.49257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74083,"mean_force":0.11812,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52772,0.00082,0.02538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18676.0,"contact_point_centroid":[0.52615,-0.01832,0.07411],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32944,"mean_force":0.05467,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5252,0.00078,0.07215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19114.0,"contact_point_centroid":[0.52614,0.01986,0.07289],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31586,"mean_force":0.05374,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52522,0.00078,0.07107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6514.0,"contact_point_centroid":[0.53356,0.03011,0.18073],"force_p95":0.14438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29178,"mean_force":0.07653,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53061,0.01132,0.18118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6692.0,"contact_point_centroid":[0.53312,-0.00773,0.18102],"force_p95":0.14462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27772,"mean_force":0.07472,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53027,0.01096,0.18169]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16056,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00088,0.02523]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.54431,0.00113,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12344,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51446,0.00039,0.2681]},{"body_a":"world","body_b":"grasp_target","contact_count":2436.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53348,0.0009,0.13233]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.57321,0.0715,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63731,0.14788,0.24748]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57321,0.0715,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63767,0.15236,0.22148]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.57321,0.0715,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.63981,0.15423,0.28056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.5308,-0.01834,0.02649],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11013,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.0238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53074,0.01994,0.02561],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09676,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.0238]},{"body_a":"left_finger","body_b":"right_finger","contact_count":950.0,"contact_point_centroid":[0.60879,0.10917,0.27861],"force_p95":0.01246,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0148,"mean_force":0.01071,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.6082,0.10917,0.27642]},{"body_a":"left_finger","body_b":"right_finger","contact_count":632.0,"contact_point_centroid":[0.63791,0.1479,0.24984],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63732,0.14789,0.24747]}],"total_contact_groups":17},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57321,0.0715,0.01602],"final_tcp_position":[0.64477,0.15682,0.3214],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.95728,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":600.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53092,0.00081,0.23417],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53846,0.00102,0.03386],"tcp_start":[0.53092,0.00081,0.23417],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16056,"subtask_id":"grasp_object","tcp_end":[0.52973,0.00086,0.02377],"tcp_start":[0.53846,0.00102,0.03386],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53685,0.00079,0.11073],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20849,"object_to_goal_dist_start":0.25053,"object_z_max":0.11063,"peak_contact_force":0.07383,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37996.0,"raw_peak_contact_force":0.74083,"subtask_id":"lift_object","tcp_end":[0.52534,0.00079,0.11945],"tcp_start":[0.52973,0.00086,0.02377],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.57321,0.0715,0.01602],"object_pos_start":[0.53685,0.00079,0.11073],"object_to_goal_dist_end":0.20902,"object_to_goal_dist_start":0.20849,"object_z_max":0.2269,"peak_contact_force":9748.95728,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15186.0,"raw_peak_contact_force":2.1859,"subtask_id":"approach_goal","tcp_end":[0.63484,0.14299,0.27293],"tcp_start":[0.52534,0.00079,0.11945],"tcp_to_object_dist_end":0.2737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.57321,0.0715,0.01602],"object_pos_start":[0.57321,0.0715,0.01602],"object_to_goal_dist_end":0.20902,"object_to_goal_dist_start":0.20902,"object_z_max":0.01602,"peak_contact_force":9748.81737,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64136,0.15331,0.22233],"tcp_start":[0.63484,0.14299,0.27293],"tcp_to_object_dist_end":0.23217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57321,0.0715,0.01602],"object_pos_start":[0.57321,0.0715,0.01602],"object_to_goal_dist_end":0.20902,"object_to_goal_dist_start":0.20902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_object","tcp_end":[0.63642,0.15194,0.24065],"tcp_start":[0.64136,0.15331,0.22233],"tcp_to_object_dist_end":0.24683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":720.0,"object_pos_end":[0.57321,0.0715,0.01602],"object_pos_start":[0.57321,0.0715,0.01602],"object_to_goal_dist_end":0.20902,"object_to_goal_dist_start":0.20902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_object","tcp_end":[0.64477,0.15682,0.3214],"tcp_start":[0.63642,0.15194,0.24065],"tcp_to_object_dist_end":0.32505,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```